# Gameini 무료 토큰을 이용한 여행지 분류 배치 처리
import requests
import json
import time
import os
from urllib.request import urlopen
from xml.etree import ElementTree as ET
from datetime import datetime

# ========================================
# 설정
# ========================================
API_KEY = 'AIzaSyCsSowN4QtGflYV8vYtd0dd4T5Vtq56bNE'  # ⚠️ 실제 Gemini API 키 노출 주의!

RSS_URLS = [
    'https://tourkongdak.tistory.com/rss',       # 투어콩닥
    'https://hst123.tistory.com/rss',            # 여행 블로그
]

OUTPUT_FOLDER = r'D:\progammers\first project personal\data'
OUTPUT_FILENAME = f'data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

WAIT_TIME = 10 # API 호출 간 대기 시간 (초)

# ========================================
# RSS 수집 함수
# ========================================
def fetch_rss(url):
    """
    RSS 피드에서 최신 5개 포스팅 수집
    """
    try:
        with urlopen(url, timeout=10) as response:
            tree = ET.parse(response)
        
        root = tree.getroot()
        posts = []
        
        for item in root.findall('.//item')[:5]:
            title = item.findtext('title', '')
            link = item.findtext('link', '')
            description = item.findtext('description', '')
            
            # 썸네일 이미지 찾기 (선택적)
            thumbnail = ''
            media_content = item.find('.//{http://search.yahoo.com/mrss/}content')
            if media_content is not None:
                thumbnail = media_content.get('url', '')
            
            posts.append({
                'title': title,
                'link': link,
                'description': description[:200],
                'thumbnail': thumbnail
            })
        
        return posts
    
    except Exception as e:
        print(f"❌ RSS 수집 실패 ({url}): {e}")
        return []

# ========================================
# Gemini API 분류 함수
# ========================================
def classify_with_gemini(title, description):
    """
    Gemini API를 호출해서 여행지 정보를 분류합니다.
    """
    # ✅ 2026년 기준 최신 모델
    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent'
    
    # ✅ 헤더에 API 키 포함
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': API_KEY
    }
    
    # 프롬프트 구성
    prompt = f"""
다음 여행 포스팅의 제목과 설명을 보고, 어느 지역/국가/도시에 대한 내용인지 분석해주세요.
반드시 JSON 형식으로만 답변해주세요:

제목: {title}
설명: {description[:200]}

JSON 형식:
{{
  "region": "아시아" (또는 "유럽", "미주", "오세아니아", "아프리카"),
  "country": "국가명",
  "city": "도시명",
  "lat": 위도(숫자),
  "lon": 경도(숫자)
}}
"""
    
    payload = {
        'contents': [
            {
                'parts': [
                    {'text': prompt}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            text = data['candidates'][0]['content']['parts'][0]['text']
            
            # JSON 파싱 (코드 블록 제거)
            text = text.replace('```json', '').replace('```', '').strip()
            location = json.loads(text)
            return location
        
        elif response.status_code == 429:
            # Rate Limit 에러 → 10분 대기 후 재시도
            print("⏳ Rate Limit 도달! 10분 대기 중...")
            time.sleep(600)
            return classify_with_gemini(title, description)
        
        else:
            print(f"⚠️ API 오류: {response.status_code} - {response.text[:100]}")
            return {
                'region': '아시아',
                'country': '한국',
                'city': '서울',
                'lat': 37.5665,
                'lon': 126.9780
            }
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 실패: {e}")
        return {
            'region': '아시아',
            'country': '한국',
            'city': '서울',
            'lat': 37.5665,
            'lon': 126.9780
        }
    
    except Exception as e:
        print(f"❌ API 호출 실패: {e}")
        return {
            'region': '아시아',
            'country': '한국',
            'city': '서울',
            'lat': 37.5665,
            'lon': 126.9780
        }

# ========================================
# 메인 함수
# ========================================
def main():
    print("=" * 60)
    print("🌍 여행 포스팅 RSS 수집 & Gemini AI 분류 시작")
    print("=" * 60)
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # ========================================
    # 1단계: RSS 수집
    # ========================================
    print("📥 1단계: RSS 피드 수집 중...\n")
    
    all_posts = []
    for idx, rss_url in enumerate(RSS_URLS, 1):
        print(f"   [{idx}/{len(RSS_URLS)}] {rss_url}")
        posts = fetch_rss(rss_url)
        all_posts.extend(posts[:5])  # 각 RSS에서 최대 5개
        print(f"       ✅ {len(posts)}개 발견!\n")
    
    print(f"📊 총 {len(all_posts)}개 포스팅 수집 완료\n")
    print("=" * 60)
    
    # ========================================
    # 2단계: Gemini AI 분류
    # ========================================
    print("🤖 2단계: Gemini AI로 지역 분류 중...\n")
    
    # API 키 확인
    if API_KEY == 'your-api-key-here':
        print("❌ 오류: API_KEY를 실제 Gemini API 키로 교체해주세요!")
        return
    
    results = []
    start_time = time.time()
    
    for idx, post in enumerate(all_posts, 1):
        # 제목 출력 (최대 50자)
        title_display = post['title'][:50] + '...' if len(post['title']) > 50 else post['title']
        print(f"[{idx:2d}/{len(all_posts)}] {title_display}")
        
        # Gemini API 호출
        location = classify_with_gemini(post['title'], post['description'])
        
        # 결과 병합
        final_post = {
            'title': post['title'],
            'link': post['link'],
            'description': post['description'],
            'thumbnail': post.get('thumbnail', ''),
            'region': location['region'],
            'country': location['country'],
            'city': location['city'],
            'lat': location['lat'],
            'lon': location['lon']
        }
        
        results.append(final_post)
        
        # 결과 출력
        print(f"       → {location['region']} / {location['country']} / {location['city']}")
        print(f"       → 좌표: ({location['lat']}, {location['lon']})\n")
        
        # ✅ Rate Limit 회피: 대기 시간
        if idx < len(all_posts):
            time.sleep(WAIT_TIME)
    
    elapsed_time = time.time() - start_time
    print("=" * 60)
    print(f"⏱️  소요 시간: {elapsed_time:.1f}초 ({elapsed_time/60:.1f}분)\n")
    
    # ========================================
    # 3단계: JSON 파일 저장
    # ========================================
    print("💾 3단계: data.json 저장 중...")
    
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    output_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILENAME)

    output_data = {
        'posts': results,
        'metadata': {
            'total_count': len(results),
            'generated_at': datetime.now().isoformat(),
            'rss_sources': RSS_URLS
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    file_size = os.path.getsize(output_path) / 1024
    print(f"✅ 저장 완료!")
    print(f"   경로: {output_path}")
    print(f"   크기: {file_size:.1f} KB\n")
    
    # ========================================
    # 4단계: 통계 출력
    # ========================================
    print("=" * 60)
    print("📊 결과 통계")
    print("=" * 60)
    
    # 지역 분포
    regions = {}
    for post in results:
        region = post.get('region', '알 수 없음')
        regions[region] = regions.get(region, 0) + 1
    
    print("\n📍 지역 분포:")
    for region, count in sorted(regions.items(), key=lambda x: x[1], reverse=True):
        print(f"   {region}: {count}개")
    
    # 국가 분포 (상위 5개)
    countries = {}
    for post in results:
        country = post.get('country', '알 수 없음')
        countries[country] = countries.get(country, 0) + 1
    
    print("\n🌏 국가 분포 (상위 5개):")
    for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   {country}: {count}개")
    
    print("\n" + "=" * 60)
    print(f"✅ 완료! data.json 파일을 확인하세요.")
    print(f"⏰ 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

# ========================================
# 실행
# ========================================
if __name__ == '__main__':
    main()
