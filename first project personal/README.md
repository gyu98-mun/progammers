RSS로 DATA를 불러오고 Gemini API로 던져서 RSS로 긁어온 글의 tags 를 뽑는 로직입니다

API_key 는 노출을 방지 하기위해 .env 로 따로 저장해 놓았습니다

Gemini API 무료 사용 한도 때문에 5개의 API_key를 준비 해놓고 사용한도 초과시 전환 하도록 구현 하였습니다