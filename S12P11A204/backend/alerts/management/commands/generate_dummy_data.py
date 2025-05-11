# 더미데이터

from django.core.management.base import BaseCommand
from drain.models import Drain, DrainCondition
from region.models import District, Block, BlockCondition
from robot_info.models import Robot
from accounts.models import CustomUser


class Command(BaseCommand):
    help = '프로젝트에 필요한 더미데이터 생성'

    def handle(self, *args, **kwargs):
        # 강남구 district 생성
        district = District.objects.create(name='강남구')
        self.stdout.write(self.style.SUCCESS('강남구 district 생성 완료'))

        # 사용자 계정 생성
        user = CustomUser.objects.create_user(
            username='test',
            password='qwer1234',
            district=district
        )
        self.stdout.write(self.style.SUCCESS('테스트 사용자 계정 생성 완료'))

        # 5개의 블록 생성 (위치 정보 없이)
        blocks = []
        for i in range(1, 6):
            block = Block.objects.create(
                name=f'Block {i}',
                Cumulative_state_score=0.0,
                Flooding_sensitivity=0.0,
                district=district
            )
            for j in range(1,5):
                BlockCondition.objects.create(
                    condition= 50+(j*10)*(-1**j),
                    block=block
                )
            blocks.append(block)
            self.stdout.write(self.style.SUCCESS(f'Block {i} 생성 완료'))

        # 각 블록의 배수구 정보 (위도, 경도)
        drain_locations = {
            'Block 1': [
                (37.49656762226077, 127.02633736707317),
                (37.49563059424602, 127.02625222573722),
                (37.495786332465805, 127.02479633322388),
                (37.49706577722628, 127.02472325088264),
                (37.4972368147752, 127.02544705415882),
            ],
            'Block 2': [
                (37.49656762226077, 127.02633736707317),
                (37.49760595035255, 127.02670243410479),
                (37.49708311359029, 127.02779917456898),
                (37.49601552836742, 127.02733796313281),
            ],
            'Block 3': [
                (37.49656762226077, 127.02633736707317),
                (37.498259436272555, 127.02554352511133),
                (37.49857960741672, 127.02404805229227),
                (37.49784081092488, 127.02390645742324),
                (37.49719642494061, 127.02471481254905),
            ],
            'Block 4': [
                (37.49656762226077, 127.02633736707317),
                (37.499025307451085, 127.02547027869248),
                (37.49881775184216, 127.02693186846754),
            ],
            'Block 5': [
                (37.49656762226077, 127.02633736707317),
                (37.495028994986576, 127.02703793590582),
                (37.4943889997236, 127.02823636544973),
                (37.49552868694765, 127.02859583265794),
            ],
        }

        # 각 블록에 대해 지정된 위치의 배수구 생성
        for block in blocks:
            for lat, lon in drain_locations[block.name]:
                drain = Drain.objects.create(
                    location_x=lat,
                    location_y=lon,
                    state_img_url='',
                    block=block
                )
                for k in range(1,5):
                    DrainCondition.objects.create(
                        condition='양호',
                        drain=drain
                    )
            self.stdout.write(self.style.SUCCESS(f'{block.name}의 배수구 생성 완료'))

        # 로봇 2개 생성
        Robot.objects.create(
            is_robot_available=True,
            robot_unavailable_reason='',
            district=district
        )
        self.stdout.write(self.style.SUCCESS('로봇 생성 완료'))

        # # 침수 이미지 업로드
        # for i in range(1, 6):
        #     block = Block.objects.filter(name=f'Block {i}')
        #     block.Flood_Image = f'images/Block{i}.png'
        #     block.save()
        # self.stdout.write(self.style.SUCCESS(f'침수 이미지 업로드 완료'))