import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 데이터 저장 디렉토리
os.makedirs('data', exist_ok=True)

# 난수 시드 설정 (재현성)
np.random.seed(42)

# 1. 일일 발전량 데이터 (365일 x 10개 발전기)
print("1. 일일 발전량 데이터 생성 중...")
dates = pd.date_range('2023-01-01', periods=365, freq='d')
generator_ids = [f'GEN_{i:03d}' for i in range(1, 11)]

daily_power = []
for date in dates:
    for gen_id in generator_ids:
        daily_power.append({
            '날짜': date,
            '발전기ID': gen_id,
            '발전량(MWh)': np.random.normal(450, 50) if np.random.random() > 0.05 else np.random.normal(200, 50),
            '가동시간(h)': np.random.normal(22, 2),
            '평균효율(%)': np.random.normal(92, 3),
            '평균온도(°C)': np.random.normal(65, 5),
            '평균압력(bar)': np.random.normal(8.5, 0.5),
        })

df_daily = pd.DataFrame(daily_power)
df_daily['발전량(MWh)'] = df_daily['발전량(MWh)'].clip(0, 600)
df_daily['가동시간(h)'] = df_daily['가동시간(h)'].clip(0, 24)
df_daily['평균효율(%)'] = df_daily['평균효율(%)'].clip(70, 98)
df_daily['평균온도(°C)'] = df_daily['평균온도(°C)'].clip(40, 90)
df_daily['평균압력(bar)'] = df_daily['평균압력(bar)'].clip(6, 11)
df_daily.to_csv('data/일일_발전량.csv', index=False, encoding='utf-8-sig')
print("✓ 일일_발전량.csv 생성 (3,650건)")

# 2. 시간별 성능 데이터 (365일 x 24시간 x 5개 발전기)
print("2. 시간별 성능 데이터 생성 중...")
hours = pd.date_range('2023-01-01', periods=365*24, freq='h')
gen_sample = [f'GEN_{i:03d}' for i in range(1, 6)]

hourly_perf = []
for hour in hours:
    for gen_id in gen_sample:
        load_factor = np.random.uniform(0.6, 1.0)
        power_output = np.random.normal(400 * load_factor, 30)
        hourly_perf.append({
            '시간': hour,
            '발전기ID': gen_id,
            '전력출력(MW)': max(0, power_output),
            '부하율(%)': load_factor * 100,
            '냉각수온도(°C)': np.random.normal(60, 4),
            '연료소비량(톤/h)': power_output / 1.5 + np.random.normal(0, 5),
            '열효율(%)': np.random.normal(91, 2.5),
        })

df_hourly = pd.DataFrame(hourly_perf)
df_hourly = df_hourly[df_hourly['전력출력(MW)'] >= 0]
df_hourly.to_csv('data/시간별_성능.csv', index=False, encoding='utf-8-sig')
print(f"✓ 시간별_성능.csv 생성 ({len(df_hourly):,}건)")

# 3. 발전기 효율 데이터
print("3. 발전기 효율 분석 데이터 생성 중...")
efficiency_data = []
for date in pd.date_range('2023-01-01', periods=52, freq='w'):  # 주간 데이터
    for gen_id in generator_ids:
        efficiency_data.append({
            '주차': date,
            '발전기ID': gen_id,
            '평균효율(%)': np.random.normal(92.5, 2),
            '최고효율(%)': np.random.normal(95, 1.5),
            '최저효율(%)': np.random.normal(88, 2),
            '목표효율(%)': 93.0,
            '달성율(%)': np.random.normal(99.5, 1.5),
        })

df_efficiency = pd.DataFrame(efficiency_data)
df_efficiency['평균효율(%)'] = df_efficiency['평균효율(%)'].clip(85, 98)
df_efficiency['달성율(%)'] = df_efficiency['달성율(%)'].clip(95, 105)
df_efficiency.to_csv('data/효율_분석.csv', index=False, encoding='utf-8-sig')
print("✓ 효율_분석.csv 생성 (520건)")

# 4. 연료 소비량 데이터
print("4. 연료 소비량 데이터 생성 중...")
fuel_data = []
for date in dates:
    for gen_id in generator_ids:
        fuel_data.append({
            '날짜': date,
            '발전기ID': gen_id,
            '일일소비량(톤)': np.random.normal(280, 40),
            '누적소비량(톤)': 0,  # 나중에 계산
            '연료단가($/톤)': np.random.normal(450, 50),
            '일일비용($)': 0,  # 나중에 계산
            '연료품질(%)': np.random.normal(95, 3),
        })

df_fuel = pd.DataFrame(fuel_data)
df_fuel['일일소비량(톤)'] = df_fuel['일일소비량(톤)'].clip(100, 450)

# 누적 소비량 계산
df_fuel = df_fuel.sort_values(['발전기ID', '날짜']).reset_index(drop=True)
df_fuel['누적소비량(톤)'] = df_fuel.groupby('발전기ID')['일일소비량(톤)'].cumsum()
df_fuel['일일비용($)'] = df_fuel['일일소비량(톤)'] * df_fuel['연료단가($/톤)']
df_fuel['연료품질(%)'] = df_fuel['연료품질(%)'].clip(85, 100)
df_fuel.to_csv('data/연료_소비.csv', index=False, encoding='utf-8-sig')
print("✓ 연료_소비.csv 생성 (3,650건)")

# 5. 유지보수 기록
print("5. 유지보수 기록 데이터 생성 중...")
maintenance_data = []
maintenance_types = ['정기점검', '부품교체', '청소', '윤활유교체', '필터교체', '센서교정', '긴급수리']
technicians = ['김기술', '이정비', '박유지', '최관리', '정보수']

for _ in range(150):
    maint_date = pd.Timestamp('2023-01-01') + timedelta(days=np.random.randint(0, 365))
    maintenance_data.append({
        '작업일자': maint_date,
        '발전기ID': np.random.choice(generator_ids),
        '작업유형': np.random.choice(maintenance_types),
        '기술자': np.random.choice(technicians),
        '작업시간(h)': np.random.uniform(0.5, 8),
        '부품비용($)': np.random.choice([0, 100, 200, 500, 1000, 2000, 5000]),
        '상태평가': np.random.choice(['양호', '보통', '주의', '불량']),
        '비고': np.random.choice(['정상완료', '추가조치필요', '부품미납', '완료'], p=[0.7, 0.15, 0.1, 0.05]),
    })

df_maint = pd.DataFrame(maintenance_data)
df_maint = df_maint.sort_values('작업일자').reset_index(drop=True)
df_maint.to_csv('data/유지보수_기록.csv', index=False, encoding='utf-8-sig')
print("✓ 유지보수_기록.csv 생성 (150건)")

# 6. 장비 상태 데이터
print("6. 장비 상태 데이터 생성 중...")
equipment_status = []
for date in pd.date_range('2023-01-01', periods=365, freq='D'):
    for gen_id in generator_ids:
        equipment_status.append({
            '날짜': date,
            '발전기ID': gen_id,
            '운영상태': np.random.choice(['정상운영', '정비중', '점검중', '고장'],
                                         p=[0.80, 0.10, 0.07, 0.03]),
            '가동상태': np.random.choice(['운전', '정지', '대기'], p=[0.75, 0.15, 0.10]),
            '최근점검일': date - timedelta(days=np.random.randint(1, 30)),
            '다음점검예정일': date + timedelta(days=np.random.randint(10, 30)),
            '발전기나이(년)': np.random.randint(2, 15),
        })

df_status = pd.DataFrame(equipment_status)
df_status.to_csv('data/장비_상태.csv', index=False, encoding='utf-8-sig')
print("✓ 장비_상태.csv 생성 (3,650건)")

# 7. 에러/경보 로그
print("7. 에러/경보 로그 데이터 생성 중...")
error_logs = []
error_types = ['온도상승', '압력이상', '진동과대', '배출가스이상', '냉각수누수',
               '센서오류', '전기회로이상', '안전장치작동', '연료부족', '기타']

for _ in range(200):
    log_time = pd.Timestamp('2023-01-01') + timedelta(hours=np.random.randint(0, 365*24))
    error_logs.append({
        '발생시간': log_time,
        '발전기ID': np.random.choice(generator_ids),
        '에러유형': np.random.choice(error_types),
        '심각도': np.random.choice(['낮음', '중간', '높음', '긴급'], p=[0.4, 0.35, 0.20, 0.05]),
        '에러코드': f'ERR_{np.random.randint(1000, 9999)}',
        '상태': np.random.choice(['해결됨', '해결됨', '해결됨', '진행중', '대기중'], p=[0.70, 0.15, 0.10, 0.03, 0.02]),
        '처리시간(분)': np.random.randint(0, 480),
    })

df_errors = pd.DataFrame(error_logs)
df_errors = df_errors.sort_values('발생시간').reset_index(drop=True)
df_errors.to_csv('data/에러_경보_로그.csv', index=False, encoding='utf-8-sig')
print("✓ 에러_경보_로그.csv 생성 (200건)")

# 8. 발전기 기본정보
print("8. 발전기 기본정보 데이터 생성 중...")
generator_info = []
for gen_id in generator_ids:
    generator_info.append({
        '발전기ID': gen_id,
        '설치위치': np.random.choice(['A동', 'B동', 'C동', 'D동']),
        '제조사': np.random.choice(['SIEMENS', 'GE', '현대중공업', '효성']),
        '모델명': f'HGT-{np.random.randint(1000, 9999)}',
        '정격용량(MW)': np.random.choice([400, 500, 600]),
        '설치년도': np.random.randint(2010, 2021),
        '연간운영시간(h)': np.random.randint(6000, 8000),
        '총발전량(MWh)': np.random.randint(3000000, 5000000),
    })

df_info = pd.DataFrame(generator_info)
df_info.to_csv('data/발전기_기본정보.csv', index=False, encoding='utf-8-sig')
print("✓ 발전기_기본정보.csv 생성 (10건)")

# 9. 월간 성과 요약
print("9. 월간 성과 요약 데이터 생성 중...")
monthly_summary = []
for month in pd.date_range('2023-01-01', periods=12, freq='ms'):
    for gen_id in generator_ids:
        monthly_summary.append({
            '연월': month,
            '발전기ID': gen_id,
            '월간발전량(MWh)': np.random.normal(13500, 1500),
            '목표발전량(MWh)': 14000,
            '달성율(%)': np.random.normal(96.5, 3),
            '월간이용률(%)': np.random.normal(75, 8),
            '평균효율(%)': np.random.normal(92.3, 2),
            '유지보수비($)': np.random.randint(1000, 10000),
            '연료비($)': np.random.randint(80000, 150000),
        })

df_monthly = pd.DataFrame(monthly_summary)
df_monthly['월간발전량(MWh)'] = df_monthly['월간발전량(MWh)'].clip(8000, 18000)
df_monthly['달성율(%)'] = df_monthly['달성율(%)'].clip(85, 105)
df_monthly['월간이용률(%)'] = df_monthly['월간이용률(%)'].clip(50, 95)
df_monthly.to_csv('data/월간_성과.csv', index=False, encoding='utf-8-sig')
print("✓ 월간_성과.csv 생성 (120건)")

print("\n✅ 모든 데이터 생성 완료!")
print("\n생성된 파일:")
for i, file in enumerate(os.listdir('data'), 1):
    filepath = os.path.join('data', file)
    size = len(pd.read_csv(filepath))
    print(f"  {i}. {file} - {size:,}건")
