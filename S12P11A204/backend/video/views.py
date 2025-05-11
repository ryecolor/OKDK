import os
import boto3
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from .models import Video
from .serializers import VideoSerializer
from botocore.exceptions import ClientError


class VideoUploadView(APIView):
    def post(self, request):
        try:
            video_file = request.FILES['video']
            
            if not video_file:
                return Response({'error': 'No video file provided'}, status=status.HTTP_400_BAD_REQUEST)

            # S3 클라이언트 생성
            s3 = boto3.client('s3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # S3에 파일 업로드
            file_name = f"videos/{video_file.name}"
            s3.upload_fileobj(video_file, settings.AWS_STORAGE_BUCKET_NAME, file_name)
            
            # S3 URL 생성
            file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_name}"
            
            # 데이터베이스에 저장
            video = Video.objects.create(
                title=video_file.name,
                file_url=file_url
            )
            
            serializer = VideoSerializer(video)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except KeyError as e:
            return Response({'error': f'Missing required field: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError as e:
            return Response({'error': f'Missing configuration: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ClientError as e:
            return Response({'error': f'AWS S3 error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VideoDownloadView(APIView):
    def post(self, request):
        video_directory = os.path.join(settings.MEDIA_ROOT, 'videos')
        os.makedirs(video_directory, exist_ok=True)

        s3 = boto3.client('s3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        downloaded_videos = []
        missing_videos = []

        for video in Video.objects.all():
            video_key = f'videos/{os.path.basename(video.file_url)}'
            dest_path = os.path.join(video_directory, os.path.basename(video.file_url))

            if not os.path.exists(dest_path):
                try:
                    s3.download_file(settings.AWS_STORAGE_BUCKET_NAME, video_key, dest_path)
                    downloaded_videos.append(video.file_url)
                    print(f"Successfully downloaded: {video.file_url}")
                except ClientError as e:
                    print(f"Error downloading {video.file_url}: {str(e)}")
                    missing_videos.append(video.file_url)
            else:
                print(f"File already exists: {dest_path}")

        return Response({
            'message': f'{len(downloaded_videos)} videos downloaded successfully, {len(missing_videos)} videos missing',
            'downloaded_videos': downloaded_videos,
            'missing_videos': missing_videos
        }, status=status.HTTP_200_OK)
    
@csrf_exempt
@api_view(['POST'])
def hardware_receive(request):
    try:
        data = request.data
        # 데이터 처리 로직
        return Response({
            'status': 'success', 
            'message': 'Data received',
            'data': data
        })
    except Exception as e:
        return Response({
            'status': 'error', 
            'message': str(e)
        }, status=400)