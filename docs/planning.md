# 부동산 매물 공유 게시판 - 기획문서

> 작성일: 2026-04-16
> 버전: v1.0

---

## 1. 프로젝트 개요

### 1.1 목적
부동산 매물을 등록하고 공유할 수 있는 웹 게시판 서비스

### 1.2 기술 스택
| 항목 | 기술 |
|------|------|
| Backend | Django 4.2 LTS (Python) |
| Database | PostgreSQL 16 |
| Frontend | Django 템플릿 + Bootstrap 5 |
| 지도 | Kakao Map API (무료) |
| 이미지 | Pillow (리사이즈/최적화) |
| 배포 | Docker + Gunicorn + Nginx |

### 1.3 사용자 유형
| 유형 | 설명 |
|------|------|
| 비회원 | 매물 조회, 검색만 가능 |
| 일반 회원 | 매물 등록/수정/삭제, 북마크, 문의 |
| 공인중개사 | 일반 회원 + 중개사 뱃지 표시 |
| 관리자 | 매물 승인/반려, 회원 관리, 신고 처리 |

---

## 2. 화면 목록

### 2.1 공통
| ID | 화면명 | URL | 설명 |
|----|--------|-----|------|
| C-01 | 메인 페이지 | `/` | 최신 매물, 추천 매물, 빠른 검색 |
| C-02 | GNB (상단 네비게이션) | - | 로고, 메뉴, 로그인/회원가입 버튼 |
| C-03 | Footer | - | 서비스 정보, 링크 |

### 2.2 회원 (accounts)
| ID | 화면명 | URL | 접근 권한 |
|----|--------|-----|----------|
| A-01 | 회원가입 | `/accounts/signup/` | 비회원 |
| A-02 | 로그인 | `/accounts/login/` | 비회원 |
| A-03 | 프로필 | `/accounts/profile/` | 회원 |
| A-04 | 프로필 수정 | `/accounts/profile/edit/` | 회원 |
| A-05 | 비밀번호 변경 | `/accounts/password/change/` | 회원 |

### 2.3 매물 (listings)
| ID | 화면명 | URL | 접근 권한 |
|----|--------|-----|----------|
| L-01 | 매물 목록 | `/listings/` | 전체 |
| L-02 | 매물 상세 | `/listings/<id>/` | 전체 |
| L-03 | 매물 등록 | `/listings/create/` | 회원 |
| L-04 | 매물 수정 | `/listings/<id>/edit/` | 작성자 |
| L-05 | 매물 삭제 확인 | `/listings/<id>/delete/` | 작성자 |
| L-06 | 내 매물 관리 | `/listings/my/` | 회원 |
| L-07 | 북마크 목록 | `/listings/bookmarks/` | 회원 |
| L-08 | 지도 보기 | `/listings/map/` | 전체 |

### 2.4 관리자
| ID | 화면명 | URL | 접근 권한 |
|----|--------|-----|----------|
| M-01 | 관리자 대시보드 | `/admin/` | 관리자 |
| M-02 | 매물 승인 관리 | `/admin/listings/property/` | 관리자 |
| M-03 | 회원 관리 | `/admin/accounts/user/` | 관리자 |
| M-04 | 신고 관리 | `/admin/listings/report/` | 관리자 |
| M-05 | 공지사항 관리 | `/admin/listings/notice/` | 관리자 |

---

## 3. 화면별 기능 정의

### 3.1 메인 페이지 (C-01)
- 히어로 섹션: 서비스 소개 + 통합 검색바
- 최신 매물 카드 8개 (2x4 그리드)
- 매물 유형별 바로가기 (아파트, 빌라, 원룸, 오피스텔, 상가)
- 공지사항 최신 3건

### 3.2 회원가입 (A-01)
- 입력 필드: 아이디, 이메일, 비밀번호, 비밀번호 확인, 이름, 전화번호
- 선택: 공인중개사 여부 체크 → 체크 시 사업자등록번호 입력
- 유효성 검증: 실시간 (아이디 중복, 비밀번호 강도, 이메일 형식)
- 약관 동의 체크박스

### 3.3 로그인 (A-02)
- 아이디 + 비밀번호 입력
- "로그인 유지" 체크박스
- 비밀번호 찾기 링크
- 회원가입 링크

### 3.4 매물 목록 (L-01)
- **검색 조건**:
  - 키워드 검색 (제목, 주소)
  - 매물 유형: 아파트 / 빌라 / 오피스텔 / 원룸 / 상가 / 토지
  - 거래 유형: 매매 / 전세 / 월세
  - 가격대: 최소~최대 (슬라이더 또는 입력)
  - 면적: 최소~최대
  - 방 수: 1~5+
  - 지역: 시/도 → 시/군/구 (2단 셀렉트)
- **정렬**: 최신순 / 가격 낮은순 / 가격 높은순 / 조회수순
- **표시 방식**: 카드뷰(기본) / 리스트뷰 전환
- **페이지네이션**: 한 페이지 12개
- 각 매물 카드: 썸네일, 거래유형 뱃지, 가격, 주소, 면적, 방수, 등록일

### 3.5 매물 상세 (L-02)
- **이미지 갤러리**: 슬라이드 형태, 클릭 시 확대
- **기본 정보**: 제목, 가격, 거래유형, 매물유형
- **상세 정보 테이블**:
  - 주소, 면적(m2/평), 층수, 방수, 화장실수
  - 입주 가능일, 관리비, 주차 여부
  - 방향, 난방 방식
- **설명**: 매물 소개 텍스트
- **지도**: 카카오맵 위치 표시
- **작성자 정보**: 이름, 전화번호, 중개사 뱃지
- **액션 버튼**: 북마크, 신고, 문의하기 (전화/메시지)
- **조회수** 표시
- 작성자 본인: 수정/삭제 버튼 노출

### 3.6 매물 등록/수정 (L-03, L-04)
- **기본 정보 (필수)**:
  - 제목 (최대 100자)
  - 매물 유형 (셀렉트)
  - 거래 유형 (셀렉트)
  - 가격 (만원 단위)
  - 보증금 / 월세 (거래유형에 따라 동적 표시)
- **상세 정보**:
  - 주소: 카카오 주소 검색 API → 자동 위도/경도 입력
  - 상세 주소 (직접 입력)
  - 면적 (m2, 평수 자동 환산 표시)
  - 층수, 방 수, 화장실 수
  - 입주 가능일 (달력 선택)
  - 관리비, 주차 가능 여부
  - 방향 (동/서/남/북)
  - 난방 방식 (개별/중앙/지역)
- **사진 업로드**:
  - 최대 10장
  - 드래그앤드롭 지원
  - 첫 번째 사진 = 대표 이미지 (변경 가능)
  - 미리보기 + 삭제 가능
- **매물 설명**: 텍스트 에디터 (줄바꿈 지원)
- **미리보기** 버튼

### 3.7 내 매물 관리 (L-06)
- 내가 등록한 매물 목록 (테이블 형태)
- 상태 표시: 대기중 / 승인 / 반려 / 거래완료
- 매물별 액션: 수정, 삭제, 거래완료 처리
- 필터: 상태별

### 3.8 북마크 목록 (L-07)
- 찜한 매물 카드 목록
- 북마크 해제 버튼
- 빈 상태: "찜한 매물이 없습니다"

### 3.9 지도 보기 (L-08)
- 전체 화면 카카오맵
- 매물 위치에 마커 표시
- 마커 클릭 → 간략 정보 팝업 (썸네일, 가격, 주소)
- 팝업에서 "상세보기" 클릭 → 상세 페이지 이동
- 좌측 사이드바: 필터 (유형, 가격대)
- 지도 이동/줌 시 해당 영역 매물만 로드

---

## 4. 데이터 모델

### 4.1 User (사용자)
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| id | AutoField | PK | |
| username | CharField(30) | Y | 아이디 |
| email | EmailField | Y | 이메일 |
| password | - | Y | Django 내장 해시 |
| name | CharField(20) | Y | 이름 |
| phone | CharField(20) | N | 전화번호 |
| profile_image | ImageField | N | 프로필 사진 |
| is_agent | BooleanField | Y | 공인중개사 여부 (기본: False) |
| business_number | CharField(20) | N | 사업자등록번호 (중개사만) |
| is_active | BooleanField | Y | 활성 상태 (기본: True) |
| created_at | DateTimeField | Y | 가입일 |
| updated_at | DateTimeField | Y | 수정일 |

### 4.2 Property (매물)
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| id | AutoField | PK | |
| author | FK(User) | Y | 등록자 |
| title | CharField(100) | Y | 제목 |
| description | TextField | Y | 매물 설명 |
| property_type | CharField(20) | Y | 매물유형 (아파트/빌라/오피스텔/원룸/상가/토지) |
| trade_type | CharField(10) | Y | 거래유형 (매매/전세/월세) |
| price | PositiveIntegerField | Y | 매매가/전세금 (만원) |
| deposit | PositiveIntegerField | N | 보증금 - 월세 (만원) |
| monthly_rent | PositiveIntegerField | N | 월세 (만원) |
| area | DecimalField(10,2) | Y | 면적 (m2) |
| address | CharField(200) | Y | 도로명 주소 |
| address_detail | CharField(100) | N | 상세 주소 |
| latitude | DecimalField(10,7) | Y | 위도 |
| longitude | DecimalField(10,7) | Y | 경도 |
| floor | PositiveSmallIntegerField | N | 층수 |
| rooms | PositiveSmallIntegerField | Y | 방 수 |
| bathrooms | PositiveSmallIntegerField | Y | 화장실 수 |
| direction | CharField(10) | N | 방향 (동/서/남/북) |
| heating | CharField(20) | N | 난방 (개별/중앙/지역) |
| parking | BooleanField | N | 주차 가능 여부 |
| maintenance_fee | PositiveIntegerField | N | 관리비 (만원) |
| available_date | DateField | N | 입주 가능일 |
| status | CharField(20) | Y | 상태 (pending/approved/rejected/completed) |
| is_available | BooleanField | Y | 거래 가능 여부 (기본: True) |
| view_count | PositiveIntegerField | Y | 조회수 (기본: 0) |
| created_at | DateTimeField | Y | 등록일 |
| updated_at | DateTimeField | Y | 수정일 |

### 4.3 PropertyImage (매물 이미지)
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| id | AutoField | PK | |
| property | FK(Property) | Y | 매물 |
| image | ImageField | Y | 이미지 파일 |
| is_thumbnail | BooleanField | Y | 대표 이미지 여부 |
| order | PositiveSmallIntegerField | Y | 정렬 순서 |
| created_at | DateTimeField | Y | 등록일 |

### 4.4 Bookmark (북마크)
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| id | AutoField | PK | |
| user | FK(User) | Y | 사용자 |
| property | FK(Property) | Y | 매물 |
| created_at | DateTimeField | Y | 등록일 |
| unique_together | (user, property) | | 중복 방지 |

### 4.5 Report (신고)
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| id | AutoField | PK | |
| reporter | FK(User) | Y | 신고자 |
| property | FK(Property) | Y | 신고 대상 매물 |
| reason | CharField(20) | Y | 사유 (허위매물/부적절내용/사기의심/기타) |
| description | TextField | N | 상세 사유 |
| status | CharField(20) | Y | 처리상태 (pending/resolved/dismissed) |
| admin_note | TextField | N | 관리자 메모 |
| created_at | DateTimeField | Y | 신고일 |
| resolved_at | DateTimeField | N | 처리일 |

### 4.6 Notice (공지사항)
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| id | AutoField | PK | |
| author | FK(User) | Y | 작성자 (관리자) |
| title | CharField(100) | Y | 제목 |
| content | TextField | Y | 내용 |
| is_pinned | BooleanField | Y | 상단 고정 여부 |
| created_at | DateTimeField | Y | 작성일 |
| updated_at | DateTimeField | Y | 수정일 |

### 4.7 ER 다이어그램

```
User 1──N Property        (사용자 → 매물 등록)
User 1──N Report           (사용자 → 신고)
User 1──N Bookmark         (사용자 → 찜)
User 1──N Notice           (관리자 → 공지)
Property 1──N PropertyImage (매물 → 사진)
Property 1──N Report        (매물 → 신고)
Property 1──N Bookmark      (매물 → 찜)
```

---

## 5. 비즈니스 규칙

### 5.1 매물 상태 흐름
```
등록 → [대기중(pending)]
         ├─ 관리자 승인 → [승인(approved)] → 목록에 노출
         ├─ 관리자 반려 → [반려(rejected)] → 사유 표시, 수정 후 재등록
         └─ 작성자 거래완료 → [완료(completed)] → "거래완료" 뱃지
```

### 5.2 권한 규칙
| 행위 | 비회원 | 회원 | 작성자 | 관리자 |
|------|--------|------|--------|--------|
| 매물 조회 | O | O | O | O |
| 매물 등록 | X | O | O | O |
| 매물 수정 | X | X | O | O |
| 매물 삭제 | X | X | O | O |
| 북마크 | X | O | O | O |
| 신고 | X | O | O | O |
| 매물 승인/반려 | X | X | X | O |
| 회원 관리 | X | X | X | O |

### 5.3 이미지 규칙
- 최대 10장, 장당 최대 10MB
- 업로드 시 자동 리사이즈 (최대 1920px)
- 허용 형식: JPG, PNG, WebP
- 매물 삭제 시 이미지 파일도 자동 삭제

### 5.4 검색/필터 규칙
- 승인(approved) 상태 매물만 목록/검색에 노출
- 거래완료 매물은 "거래완료" 뱃지와 함께 표시 (필터로 숨기기 가능)
- 가격 필터: 거래유형에 따라 기준 금액 변경

---

## 6. 개발 단계 (Phase)

| Phase | 내용 | 산출물 |
|-------|------|--------|
| **1** | 프로젝트 세팅 + DB | Django 프로젝트, PostgreSQL 연결 |
| **2** | 회원 기능 | 가입, 로그인, 프로필 |
| **3** | 매물 CRUD | 등록, 목록, 상세, 수정, 삭제 |
| **4** | 사진 업로드 | 복수 이미지, 리사이즈, 삭제 |
| **5** | 검색/필터 | 유형, 가격, 지역, 정렬 |
| **6** | 지도 연동 | 카카오맵 주소검색, 마커, 지도뷰 |
| **7** | 북마크 + 신고 | 찜하기, 신고 접수 |
| **8** | 관리자 기능 | Django Admin 커스터마이징 |
| **9** | 공지사항 | 공지 CRUD + 메인 노출 |
| **10** | 배포 준비 | Docker, Gunicorn, Nginx |
