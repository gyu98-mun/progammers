# Gemini 무료 토큰을 이용한 여행지 분류 배치 처리
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
API_KEY = 'AIzaSyCvLe9zvt0G_ZOkvWYkHPZQB9i8PBtcrXA'  # ⚠️ 실제 Gemini API 키로 교체하세요!

RSS_URLS = [
    'https://tourkongdak.tistory.com/rss',  # 투어콩닥
]

OUTPUT_FOLDER = r'D:\progammers\first project personal\data'
OUTPUT_FILENAME = f'data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

WAIT_TIME = 10  # API 호출 간 대기 시간 (초)

# ========================================
# 기본값 (API 실패 시 사용)
# ========================================
DEFAULT_LOCATION = {
    'region': '서울/경기',
    'city': '서울',
    'lat': 37.5665,
    'lon': 126.9780,
    'travelType': ['도시'],
    'season': '사계절',
    'style': ['가족여행'],
    'activities': [],
    'budget': '보통',
    'difficulty': None,
    'highlights': [],
    'tags': []
}

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
                'description': description[:300],  # 300자로 제한
                'thumbnail': thumbnail
            })
        
        return posts
    
    except Exception as e:
        print(f"❌ RSS 수집 실패 ({url}): {e}")
        return []

# ========================================
# Gemini API 분류 함수
# ========================================
def classify_with_gemini(title, description, retry_count=0, max_retries=3):
    """
    Gemini API를 호출해서 여행지 정보를 분류합니다.
    """
    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent'
    
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': API_KEY
    }
    
    # ✅ 프롬프트 단순화 (타임아웃 방지)
    prompt = f"""
여행 포스팅 분석 후 JSON만 반환:

제목: {title}
내용: {description}

JSON 형식 (이 형식 그대로):
{{
  "region": "경상",
  "city": "청송",
  "lat": 36.4367,
  "lon": 129.0572,
  "travelType": ["자연", "힐링"],
  "season": "겨울",
  "style": ["가족여행"],
  "activities": ["등산/트레킹", "온천/스파"],
  "budget": "보통",
  "difficulty": "쉬움",
  "highlights": ["장소1", "장소2", "장소3"],
  "tags": ["태그1", "태그2", "태그3"]
}}

카테고리:
- region: 서울/경기, 강원, 충청, 경상, 전라, 제주
- travelType: 자연, 문화, 힐링, 액티비티, 맛집, 도시
- season: 봄, 여름, 가을, 겨울, 사계절
- style: 가족여행, 커플여행, 혼자여행, 친구여행
- activities: 등산/트레킹, 사진촬영, 캠핑/글램핑, 온천/스파, 축제/이벤트, 드라이브, 카페투어, 야경감상
- budget: 무료, 저렴, 보통, 고급
- difficulty: 쉬움, 보통, 어려움 (액티비티 아니면 null)
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
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            text = data['candidates'][0]['content']['parts'][0]['text']
            
            # 디버깅: 응답 확인
            print(f"   🔍 응답 샘플: {text[:100]}...")
            
            # JSON 파싱 (코드 블록 제거)
            text = text.replace('```json', '').replace('```', '').strip()
            location = json.loads(text)
            
            print(f"   ✅ 파싱 성공")
            return location
        
        elif response.status_code == 429:
            # Rate Limit 에러
            if retry_count < max_retries:
                print(f"   ⏳ Rate Limit! 재시도 {retry_count+1}/{max_retries} (60초 대기)")
                time.sleep(60)
                return classify_with_gemini(title, description, retry_count+1, max_retries)
            else:
                print(f"   ❌ 최대 재시도 초과 → 기본값 반환")
                return DEFAULT_LOCATION
        
        else:
            print(f"   ⚠️ API 오류: {response.status_code}")
            return DEFAULT_LOCATION
    
    except requests.exceptions.Timeout:
        # 타임아웃 에러
        if retry_count < max_retries:
            print(f"   ⏱️ 타임아웃! 재시도 {retry_count+1}/{max_retries} (10초 대기)")
            time.sleep(10)
            return classify_with_gemini(title, description, retry_count+1, max_retries)
        else:
            print(f"   ❌ 최대 재시도 초과 → 기본값 반환")
            return DEFAULT_LOCATION
    
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON 파싱 실패: {e}")
        print(f"   응답 내용: {text[:200]}")
        return DEFAULT_LOCATION
    
    except Exception as e:
        print(f"   ❌ API 호출 실패: {e}")
        return DEFAULT_LOCATION

# ========================================
# 메인 함수
# ========================================
def main():
    print("=" * 60)
    print("🌍 여행 포스팅 RSS 수집 & Gemini AI 분류 시작")
    print("=" * 60)
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # API 키 확인
    if not API_KEY or API_KEY == 'your-api-key-here':
        print("❌ 오류: API_KEY를 실제 Gemini API 키로 교체해주세요!")
        print("   파일 상단의 API_KEY = '' 부분을 수정하세요.\n")
        return
    
    print(f"🔑 API 키 확인: {API_KEY[:10]}...{API_KEY[-5:]}\n")
    
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
    
    results = []
    start_time = time.time()
    
    for idx, post in enumerate(all_posts, 1):
        # 제목 출력 (최대 50자)
        title_display = post['title'][:50] + '...' if len(post['title']) > 50 else post['title']
        print(f"[{idx:2d}/{len(all_posts)}] {title_display}")
        
        # Gemini API 호출
        location = classify_with_gemini(post['title'], post['description'])
        
        # ✅ 결과 병합 (안전하게 .get() 사용)
        final_post = {
            'title': post['title'],
            'link': post['link'],
            'description': post['description'],
            'thumbnail': post.get('thumbnail', ''),
            
            # AI 분석 결과
            'region': location.get('region', '서울/경기'),
            'city': location.get('city', '서울'),
            'lat': location.get('lat', 37.5665),
            'lon': location.get('lon', 126.9780),
            'travelType': location.get('travelType', []),
            'season': location.get('season', '사계절'),
            'style': location.get('style', []),
            'activities': location.get('activities', []),
            'budget': location.get('budget', '보통'),
            'difficulty': location.get('difficulty', None),
            'highlights': location.get('highlights', []),
            'tags': location.get('tags', [])
        }
        
        results.append(final_post)
        
        # 결과 출력
        print(f"       → {final_post['region']} / {final_post['city']}")
        print(f"       → 좌표: ({final_post['lat']}, {final_post['lon']})")
        print(f"       → 타입: {', '.join(final_post['travelType'])}")
        print(f"       → 태그: {', '.join(final_post['tags'][:3])}\n")
        
        # Rate Limit 회피: 대기 시간
        if idx < len(all_posts):
            print(f"   ⏳ {WAIT_TIME}초 대기...\n")
            time.sleep(WAIT_TIME)
    
    elapsed_time = time.time() - start_time
    print("=" * 60)
    print(f"⏱️  소요 시간: {elapsed_time:.1f}초 ({elapsed_time/60:.1f}분)\n")
    
    # ========================================
    # 3단계: JSON 파일 저장
    # ========================================
    print("💾 3단계: JSON 저장 중...")
    
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    output_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILENAME)

    output_data = {
        'posts': results,
        'metadata': {
            'total_count': len(results),
            'generated_at': datetime.now().isoformat(),
            'rss_sources': RSS_URLS,
            'version': '2.0'
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
    
    # 여행 타입 분포
    travel_types = {}
    for post in results:
        for t in post.get('travelType', []):
            travel_types[t] = travel_types.get(t, 0) + 1
    
    print("\n🎯 여행 타입 분포:")
    for ttype, count in sorted(travel_types.items(), key=lambda x: x[1], reverse=True):
        print(f"   {ttype}: {count}개")
    
    # 계절 분포
    seasons = {}
    for post in results:
        season = post.get('season', '알 수 없음')
        seasons[season] = seasons.get(season, 0) + 1
    
    print("\n🌸 계절 분포:")
    for season, count in sorted(seasons.items(), key=lambda x: x[1], reverse=True):
        print(f"   {season}: {count}개")
    
    print("\n" + "=" * 60)
    print(f"✅ 완료! data.json 파일을 확인하세요.")
    print(f"⏰ 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

# ========================================
# 실행
# ========================================
if __name__ == '__main__':
    main()
