# 주기적으로 재무제표, 환율 데이터를 스크래핑

## 준비사항

1. 도커 설치 및 build_image.sh 실행 - 파이썬 환경을 도커 이미지로 구성
2. 에러 로그를 위한 errors 폴더 생성
3. .env 파일에 DART_API_KEY와 EXCHANGE_RATE_API_KEY를 설정
4. 크론탭에 매월 첫날 activate_exchange_rate_scrape.sh, 매일 activate_finance_scrape.sh 실행하도록 등록
   - sh파일에 (pwd)로 된 부분은 이 레포지토리의 최상 경로를 가르키도록 바꿔주기
