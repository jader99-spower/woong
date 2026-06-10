import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import io

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 데이터 저장 디렉토리
os.makedirs('data', exist_ok=True)

# 난수 시드 설정 (재현성)
np.random.seed(42)

def calculate_ambient_temp(timestamp):
    """외기 온도 계산: 계절별 + 시간별 특성"""
    day_of_year = timestamp.dayofyear

    # 계절 주기 (겨울철 -10도, 하절기 40도)
    seasonal_temp = (-10 + 40) / 2 + (40 - (-10)) / 2 * np.sin(2 * np.pi * (day_of_year - 80) / 365)

    # 일일 주기 (새벽 4시 최저, 낮 2시 최고)
    daily_variation = 8 * np.sin(2 * np.pi * (timestamp.hour - 4) / 24)

    ambient_temp = seasonal_temp + daily_variation + np.random.normal(0, 0.5)
    return ambient_temp

def calculate_efficiency(ambient_temp):
    """발전기 효율 계산: 15도에서 최고 53%, 이탈시 감소 (최저 49%)"""
    k = 4 / 225
    efficiency = 53 - k * (ambient_temp - 15) ** 2
    efficiency = max(49, min(53, efficiency))
    return efficiency + np.random.normal(0, 0.2)

def calculate_power_output(ambient_temp):
    """발전기 출력 계산: 15도 기준 835MW"""
    if ambient_temp >= 15:
        power = 835 - 4.2 * (ambient_temp - 15)
        power = max(730, power)
    else:
        power = 835 - 2.2 * (ambient_temp - 15)
        power = min(890, power)

    power += np.random.normal(0, 3)
    return power

print("=" * 60)
print("발전기 성능 관리 데이터 생성 (v2.0 - 온도 특성 반영)")
print("=" * 60)

# 1. 시간별 성능 데이터 (365일 x 24시간 x 5개 발전기)
print("\n[1/9] 시간별 성능 데이터 생성 중...")
hours_range = pd.date_range('2023-01-01', periods=365*24, freq='h')
gen_ids = [f'GEN_{i:03d}' for i in range(1, 6)]

hourly_records = []
for timestamp in hours_range:
    ambient_temp = calculate_ambient_temp(timestamp)

    for gen_id in gen_ids:
        efficiency = calculate_efficiency(ambient_temp)
        power_output = calculate_power_output(ambient_temp)
        fuel_consumption = power_output / 1.2 + np.random.normal(0, 5)

        hourly_records.append({
            'timestamp': timestamp,
            'gen_id': gen_id,
            'ambient_temp': ambient_temp,
            'power_output': max(0, power_output),
            'efficiency': efficiency,
            'load_rate': (power_output / 835) * 100,
            'coolant_temp': ambient_temp + 50 + np.random.normal(0, 2),
            'fuel_consumption': max(0, fuel_consumption),
            'thermal_efficiency': efficiency - np.random.uniform(0, 2),
        })

df_hourly = pd.DataFrame(hourly_records)
df_hourly_export = df_hourly.copy()
df_hourly_export.columns = ['시간', '발전기ID', '외기온도(°C)', '전력출력(MW)', '효율(%)',
                             '부하율(%)', '냉각수온도(°C)', '연료소비량(톤/h)', '열효율(%)']
df_hourly_export.to_csv('data/시간별_성능.csv', index=False, encoding='utf-8-sig')
print(f"   생성: 시간별_성능.csv ({len(df_hourly):,}건)")

# 2. 일일 발전량 데이터
print("[2/9] 일일 발전량 데이터 생성 중...")
dates_range = pd.date_range('2023-01-01', periods=365, freq='D')
gen_all = [f'GEN_{i:03d}' for i in range(1, 11)]

daily_records = []
for date in dates_range:
    for gen_id in gen_all:
        day_records = df_hourly[
            (df_hourly['timestamp'].dt.date == date.date()) &
            (df_hourly['gen_id'] == gen_id)
        ]

        if len(day_records) == 0:
            continue

        daily_power = day_records['power_output'].sum() / 1000
        avg_efficiency = day_records['efficiency'].mean()
        avg_temp = day_records['ambient_temp'].mean()
        operating_hours = (day_records['power_output'] > 10).sum()

        daily_records.append({
            'date': date,
            'gen_id': gen_id,
            'daily_power': daily_power,
            'operating_hours': operating_hours,
            'avg_efficiency': avg_efficiency,
            'avg_temp': avg_temp,
            'avg_coolant': avg_temp + 50,
            'avg_pressure': 8.5 + np.random.normal(0, 0.3),
        })

df_daily = pd.DataFrame(daily_records)
df_daily_export = df_daily.copy()
df_daily_export.columns = ['날짜', '발전기ID', '발전량(MWh)', '가동시간(h)', '평균효율(%)',
                            '평균외기온도(°C)', '평균냉각수온도(°C)', '평균압력(bar)']
df_daily_export.to_csv('data/일일_발전량.csv', index=False, encoding='utf-8-sig')
print(f"   생성: 일일_발전량.csv ({len(df_daily):,}건)")

# 3. 효율 분석 데이터 (주간)
print("[3/9] 효율 분석 데이터 생성 중...")
weekly_dates = pd.date_range('2023-01-01', periods=52, freq='W')

weekly_records = []
for week_start in weekly_dates:
    for gen_id in gen_all:
        week_records = df_hourly[
            (df_hourly['timestamp'] >= week_start) &
            (df_hourly['timestamp'] < week_start + timedelta(days=7)) &
            (df_hourly['gen_id'] == gen_id)
        ]

        if len(week_records) == 0:
            continue

        weekly_records.append({
            'week_start': week_start,
            'gen_id': gen_id,
            'avg_eff': week_records['efficiency'].mean(),
            'max_eff': week_records['efficiency'].max(),
            'min_eff': week_records['efficiency'].min(),
            'target_eff': 52.0,
            'achieve_rate': (week_records['efficiency'].mean() / 52.0) * 100,
        })

df_weekly = pd.DataFrame(weekly_records)
df_weekly_export = df_weekly.copy()
df_weekly_export.columns = ['주차', '발전기ID', '평균효율(%)', '최고효율(%)', '최저효율(%)',
                             '목표효율(%)', '달성율(%)']
df_weekly_export.to_csv('data/효율_분석.csv', index=False, encoding='utf-8-sig')
print(f"   생성: 효율_분석.csv ({len(df_weekly):,}건)")

# 4. 연료 소비량 데이터
print("[4/9] 연료 소비량 데이터 생성 중...")
fuel_records = []
cumsum_by_gen = {gen: 0 for gen in gen_all}

for date in dates_range:
    for gen_id in gen_all:
        day_records = df_hourly[
            (df_hourly['timestamp'].dt.date == date.date()) &
            (df_hourly['gen_id'] == gen_id)
        ]

        if len(day_records) == 0:
            continue

        daily_consumption = day_records['fuel_consumption'].sum()
        cumsum_by_gen[gen_id] += daily_consumption
        fuel_price = 450 + np.random.normal(0, 20)

        fuel_records.append({
            'date': date,
            'gen_id': gen_id,
            'daily_fuel': daily_consumption,
            'cumsum_fuel': cumsum_by_gen[gen_id],
            'fuel_price': fuel_price,
            'daily_cost': daily_consumption * fuel_price,
            'fuel_quality': np.random.normal(95, 2),
        })

df_fuel = pd.DataFrame(fuel_records)
df_fuel_export = df_fuel.copy()
df_fuel_export.columns = ['날짜', '발전기ID', '일일소비량(톤)', '누적소비량(톤)',
                          '연료단가($/톤)', '일일비용($)', '연료품질(%)']
df_fuel_export['연료품질(%)'] = df_fuel_export['연료품질(%)'].clip(90, 100)
df_fuel_export.to_csv('data/연료_소비.csv', index=False, encoding='utf-8-sig')
print(f"   생성: 연료_소비.csv ({len(df_fuel):,}건)")

# 5. 유지보수 기록
print("[5/9] 유지보수 기록 데이터 생성 중...")
maintenance_types = ['정기점검', '부품교체', '청소', '윤활유교체', '필터교체', '센서교정', '긴급수리']
technicians = ['김기술', '이정비', '박유지', '최관리', '정보수']

maint_records = []
for _ in range(150):
    maint_date = pd.Timestamp('2023-01-01') + timedelta(days=np.random.randint(0, 365))
    maint_records.append({
        'work_date': maint_date,
        'gen_id': np.random.choice(gen_all),
        'work_type': np.random.choice(maintenance_types),
        'technician': np.random.choice(technicians),
        'work_hours': np.random.uniform(0.5, 8),
        'parts_cost': np.random.choice([0, 100, 200, 500, 1000, 2000, 5000]),
        'status': np.random.choice(['양호', '보통', '주의', '불량']),
        'remarks': np.random.choice(['정상완료', '추가조치필요', '부품미납', '완료'], p=[0.7, 0.15, 0.1, 0.05]),
    })

df_maint = pd.DataFrame(maint_records)
df_maint_export = df_maint.copy()
df_maint_export.columns = ['작업일자', '발전기ID', '작업유형', '기술자', '작업시간(h)',
                            '부품비용($)', '상태평가', '비고']
df_maint_export.to_csv('data/유지보수_기록.csv', index=False, encoding='utf-8-sig')
print(f"   생성: 유지보수_기록.csv ({len(df_maint):,}건)")

# 6. 장비 상태 데이터
print("[6/9] 장비 상태 데이터 생성 중...")
status_records = []
for date in dates_range:
    for gen_id in gen_all:
        status_records.append({
            'date': date,
            'gen_id': gen_id,
            'operation_status': np.random.choice(['정상운영', '정비중', '점검중', '고장'],
                                                 p=[0.80, 0.10, 0.07, 0.03]),
            'running_status': np.random.choice(['운전', '정지', '대기'], p=[0.75, 0.15, 0.10]),
            'last_check': date - timedelta(days=np.random.randint(1, 30)),
            'next_check': date + timedelta(days=np.random.randint(10, 30)),
            'generator_age': np.random.randint(2, 15),
        })

df_status = pd.DataFrame(status_records)
df_status_export = df_status.copy()
df_status_export.columns = ['날짜', '발전기ID', '운영상태', '가동상태', '최근점검일',
                             '다음점검예정일', '발전기나이(년)']
df_status_export.to_csv('data/장비_상태.csv', index=False, encoding='utf-8-sig')
print(f"   생성: 장비_상태.csv ({len(df_status):,}건)")

# 7. 에러/경보 로그
print("[7/9] 에러/경보 로그 데이터 생성 중...")
error_types = ['온도상승', '압력이상', '진동과대', '배출가스이상', '냉각수누수',
               '센서오류', '전기회로이상', '안전장치작동', '연료부족', '기타']

error_records = []
for _ in range(200):
    log_time = pd.Timestamp('2023-01-01') + timedelta(hours=np.random.randint(0, 365*24))
    error_records.append({
        'error_time': log_time,
        'gen_id': np.random.choice(gen_all),
        'error_type': np.random.choice(error_types),
        'severity': np.random.choice(['낮음', '중간', '높음', '긴급'], p=[0.4, 0.35, 0.20, 0.05]),
        'error_code': f'ERR_{np.random.randint(1000, 9999)}',
        'status': np.random.choice(['해결됨', '진행중', '대기중'], p=[0.70, 0.20, 0.10]),
        'process_time': np.random.randint(0, 480),
    })

df_errors = pd.DataFrame(error_records)
df_errors_export = df_errors.copy()
df_errors_export.columns = ['발생시간', '발전기ID', '에러유형', '심각도', '에러코드',
                             '상태', '처리시간(분)']
df_errors_export.to_csv('data/에러_경보_로그.csv', index=False, encoding='utf-8-sig')
print(f"   생성: 에러_경보_로그.csv ({len(df_errors):,}건)")

# 8. 발전기 기본정보
print("[8/9] 발전기 기본정보 데이터 생성 중...")
info_records = []
for gen_id in gen_all:
    info_records.append({
        'gen_id': gen_id,
        'location': np.random.choice(['A동', 'B동', 'C동', 'D동']),
        'manufacturer': np.random.choice(['SIEMENS', 'GE', '현대중공업', '효성']),
        'model': f'HGT-{np.random.randint(1000, 9999)}',
        'capacity': 835,
        'install_year': np.random.randint(2010, 2021),
        'annual_hours': np.random.randint(6000, 8000),
        'total_power': 0.0,
    })

df_info = pd.DataFrame(info_records)
# 총발전량 계산
for idx, row in df_info.iterrows():
    total = df_daily[df_daily['gen_id'] == row['gen_id']]['daily_power'].sum()
    df_info.loc[idx, 'total_power'] = total

df_info_export = df_info.copy()
df_info_export.columns = ['발전기ID', '설치위치', '제조사', '모델명', '정격용량(MW)',
                           '설치년도', '연간운영시간(h)', '총발전량(MWh)']
df_info_export.to_csv('data/발전기_기본정보.csv', index=False, encoding='utf-8-sig')
print(f"   생성: 발전기_기본정보.csv ({len(df_info):,}건)")

# 9. 월간 성과 요약
print("[9/9] 월간 성과 요약 데이터 생성 중...")
monthly_dates = pd.date_range('2023-01-01', periods=12, freq='MS')
monthly_records = []

for month_start in monthly_dates:
    month_end = month_start + timedelta(days=31)

    for gen_id in gen_all:
        month_data = df_daily[
            (df_daily['date'] >= month_start) &
            (df_daily['date'] < month_end) &
            (df_daily['gen_id'] == gen_id)
        ]

        if len(month_data) == 0:
            continue

        monthly_power = month_data['daily_power'].sum()
        target_power = 14000

        monthly_records.append({
            'month': month_start,
            'gen_id': gen_id,
            'monthly_power': monthly_power,
            'target_power': target_power,
            'achieve_rate': (monthly_power / target_power) * 100,
            'util_rate': (month_data['operating_hours'].sum() / (31*24)) * 100,
            'avg_eff': month_data['avg_efficiency'].mean(),
            'maint_cost': np.random.randint(1000, 10000),
            'fuel_cost': month_data['date'].count() * 300,
        })

df_monthly = pd.DataFrame(monthly_records)
df_monthly_export = df_monthly.copy()
df_monthly_export.columns = ['연월', '발전기ID', '월간발전량(MWh)', '목표발전량(MWh)',
                              '달성율(%)', '월간이용률(%)', '평균효율(%)',
                              '유지보수비($)', '연료비($)']
df_monthly_export.to_csv('data/월간_성과.csv', index=False, encoding='utf-8-sig')
print(f"   생성: 월간_성과.csv ({len(df_monthly):,}건)")

# 10. 온도 특성 데이터 (검증용)
print("[10/10] 온도 특성 데이터 생성 중...")
temp_records = []
for date in pd.date_range('2023-01-01', periods=365, freq='D'):
    for hour in [0, 4, 8, 12, 14, 18, 20]:
        ts = pd.Timestamp(year=date.year, month=date.month, day=date.day, hour=hour)
        temp = calculate_ambient_temp(ts)
        temp_records.append({
            'date': date,
            'hour': hour,
            'ambient_temp': temp,
        })

df_temp = pd.DataFrame(temp_records)
df_temp_export = df_temp.copy()
df_temp_export.columns = ['날짜', '시간', '외기온도(°C)']
df_temp_export.to_csv('data/온도_특성.csv', index=False, encoding='utf-8-sig')
print(f"   생성: 온도_특성.csv ({len(df_temp):,}건)")

print("\n" + "=" * 60)
print("생성 완료!")
print("=" * 60)
print("\n생성된 파일 목록:")
file_count = 1
for file in sorted(os.listdir('data')):
    filepath = os.path.join('data', file)
    try:
        df = pd.read_csv(filepath)
        size = len(df)
        print(f"  {file_count:2d}. {file:<25s} {size:>7,}건")
        file_count += 1
    except:
        pass

print("\n특징:")
print("  온도 특성:")
print("    - 계절별: 겨울 -10도 ~ 하절기 40도 (자연적 변화)")
print("    - 일일: 새벽 4시 최저, 낮 2시 최고 (일교차 약 16도)")
print("  발전기 효율:")
print("    - 15도 기준: 최고 53%")
print("    - 온도 이탈: 감소 (최저 49%)")
print("  발전기 출력:")
print("    - 15도 기준: 835MW (표준)")
print("    - 고온: 최저 730MW (40도)")
print("    - 저온: 최대 890MW (-10도)")
