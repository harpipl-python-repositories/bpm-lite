from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import FolderSerializer, BpmnUploadSerializer
from .models import Folder
from .bpmn.parser import parse_bpmn
from .bpmn.mapper import save_bpmn_to_db
from django.conf import settings
import zipfile
import io
import xml.etree.ElementTree as ET


class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    lookup_field = "logical_id"
    lookup_url_kwarg = "logical_id"

    @classmethod
    def validate_bpmn_content(cls, content: bytes) -> None:
        """Validate basic BPMN structure and required elements"""
        try:
            root = ET.fromstring(content)
            
            # Sprawdzenie przestrzeni nazw BPMN
            bpmn_ns = "{http://www.omg.org/spec/BPMN/20100524/MODEL}"
            if not root.tag.startswith(bpmn_ns):
                raise ValueError("Invalid BPMN namespace")
            
            # Sprawdzenie elementu definitions
            if not root.tag.endswith("}definitions"):
                raise ValueError("Root element must be 'definitions'")
            
            # Sprawdzenie elementu process
            process = root.find(f".//{bpmn_ns}process")
            if process is None:
                raise ValueError("No process element found in BPMN file")
            
            # Sprawdzenie wymaganych atrybutów process
            if "id" not in process.attrib:
                raise ValueError("Process element must have an id attribute")
            if "name" not in process.attrib:
                raise ValueError("Process element must have a name attribute")
            
            # Sprawdzenie czy process ma jakieś elementy
            if not list(process):
                raise ValueError("Process element is empty")
            
            # Sprawdzenie czy są jakieś taski lub gateways
            has_tasks = process.findall(f".//{bpmn_ns}task") or process.findall(f".//{bpmn_ns}serviceTask")
            has_gateways = process.findall(f".//{bpmn_ns}gateway")
            has_events = process.findall(f".//{bpmn_ns}startEvent") or process.findall(f".//{bpmn_ns}endEvent")
            
            if not (has_tasks or has_gateways or has_events):
                raise ValueError("Process must contain at least one task, gateway, or event")
            
            # Sprawdzenie czy są jakieś sequence flows
            if not process.findall(f".//{bpmn_ns}sequenceFlow"):
                raise ValueError("Process must contain at least one sequence flow")
                
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {str(e)}")
        except Exception as e:
            raise ValueError(f"BPMN validation error: {str(e)}")

    @classmethod
    def unzip_file(cls, uploaded_file) -> list[tuple[str, bytes]]:
        processed_files = []
        try:
            with zipfile.ZipFile(io.BytesIO(uploaded_file.read())) as zip_ref:
                if not zip_ref.namelist():
                    raise ValueError("ZIP file is empty")
                
                if len(zip_ref.namelist()) > settings.MAX_FILES_IN_ZIP:
                    raise ValueError(f"ZIP file contains too many files (max {settings.MAX_FILES_IN_ZIP})")
                
                # Sprawdzenie czy są jakieś pliki BPMN w archiwum
                bpmn_files = [f for f in zip_ref.namelist() if f.endswith(".bpmn")]
                if not bpmn_files:
                    raise ValueError("No BPMN files found in ZIP archive")
                
                for filename in bpmn_files:
                    try:
                        content = zip_ref.read(filename)
                        cls.validate_bpmn_content(content)  # Walidacja zawartości BPMN
                        processed_files.append((filename, content))
                    except Exception as e:
                        raise ValueError(f"Error processing file {filename}: {str(e)}")
                    
            return processed_files
        except zipfile.BadZipFile:
            raise ValueError("Invalid or corrupted ZIP file")
        except Exception as e:
            raise ValueError(f"Error processing ZIP file: {str(e)}")

    def create(self, request, *args, **kwargs):
        """Override create method to handle BPMN file uploads"""
        serializer = BpmnUploadSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uploaded_file = request.FILES["file"]
                
                # Sprawdzenie rozmiaru pliku
                max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
                if uploaded_file.size > max_size_bytes:
                    return Response(
                        {"error": f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Sprawdzenie czy folder o takiej nazwie już istnieje
                folder_name = serializer.validated_data["folder_name"]
                if Folder.objects.filter(name=folder_name).exists():
                    return Response(
                        {"error": f"Folder with name '{folder_name}' already exists"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                folder = Folder.objects.create(
                    name=folder_name,
                    description=serializer.validated_data.get("description", None),
                )

                try:
                    if uploaded_file.name.endswith(".zip"):
                        processed_files = self.unzip_file(uploaded_file)
                    else:
                        if not uploaded_file.name.endswith(".bpmn"):
                            raise ValueError("File must be either .bpmn or .zip")
                        try:
                            content = uploaded_file.read()
                            self.validate_bpmn_content(content)  # Walidacja zawartości BPMN
                            processed_files = [(uploaded_file.name, content)]
                        except Exception as e:
                            raise ValueError(f"Error reading file: {str(e)}")

                    successful_files = []
                    failed_files = []

                    for filename, bpmn_content in processed_files:
                        try:
                            process_def = parse_bpmn(bpmn_content)
                            save_bpmn_to_db(process_def, folder)
                            successful_files.append(filename)
                        except Exception as e:
                            failed_files.append({"filename": filename, "error": str(e)})

                    if not successful_files and failed_files:
                        folder.delete()
                        return Response(
                            {"error": "All files failed to process", "details": failed_files},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    return Response(
                        {
                            "message": "BPMN file(s) processed",
                            "folder_id": folder.logical_id,
                            "folder_name": folder.name,
                            "successful_files": successful_files,
                            "failed_files": failed_files,
                            "total_processed": len(successful_files),
                            "total_failed": len(failed_files)
                        },
                        status=status.HTTP_201_CREATED,
                    )
                except Exception as e:
                    folder.delete()
                    raise e

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
