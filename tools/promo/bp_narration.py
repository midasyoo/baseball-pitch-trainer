# -*- coding: utf-8 -*-
"""내레이션 대본 — 스토리보드(bp_story.py) 타임라인에 맞춰 배치한다.

대본은 자막을 그대로 읽지 않는다. 자막이 설명을 맡고 내레이션은 짧게 찌른다.
한국어 신경망 TTS 는 자연스러운 속도에서 초당 5~6음절이므로, limit 초에
들어가려면 대략 limit x 5 음절을 넘기지 않아야 한다.
"""

VOICE = 'ko-KR-InJoonNeural'      # 남성 · 차분한 해설 톤
PITCH = '-2Hz'
RATES = ['+0%', '+6%', '+12%', '+18%']   # 이 이상은 홍보 톤이 무너져 쓰지 않는다

LINES = [
  dict(start= 0.5, limit=3.2, text='원리를 눈으로 보고, 손으로 따라 합니다.'),
  dict(start= 4.6, limit=2.2, text='첫째, 원리 이해.'),
  dict(start= 7.4, limit=3.4, text='어느 손가락이 실밥 어디에 닿는가.'),
  dict(start=11.4, limit=4.3, text='엄지가 먼저, 손끝이 나중에. 그 순서가 회전입니다.'),
  dict(start=16.4, limit=3.4, text='회전축이 기울면 공은 옆으로 미끄러집니다.'),
  dict(start=20.4, limit=3.4, text='세트부터 팔로스루까지, 힘이 만들어지는 순서.'),
  dict(start=24.4, limit=3.4, text='스트라이크 존까지, 공이 그리는 실제 경로.'),
  dict(start=28.4, limit=3.4, text='타석에서는 이렇게 보입니다.'),
  dict(start=32.4, limit=5.2, text='투심 패스트볼, 싱커, 슬라이더.'),
  dict(start=38.4, limit=5.2, text='커브볼, 포크볼, 너클볼. 모두 열네 개 구종.'),
  dict(start=44.3, limit=2.0, text='둘째, 실제 연습.'),
  dict(start=46.4, limit=3.1, text='삼디 그립 그대로, 진짜 공으로.'),
  dict(start=50.0, limit=3.2, text='손을 찍으면 에이아이가 손가락을 읽습니다.'),
  dict(start=53.6, limit=3.2, text='변화구 반복 투구는 지도자와 함께.'),
  dict(start=57.3, limit=2.5, text='설치 없이, 브라우저에서 바로.'),
]

if __name__ == '__main__':
    tot = 0
    for i, l in enumerate(LINES):
        syl = len([c for c in l['text'] if '가' <= c <= '힣'])
        tot += syl
        mark = '  ' if syl <= l['limit']*5.6 else '길'
        print('%2d %s %5.1fs (~%.1fs)  %2d음절  %s' % (i, mark, l['start'], l['limit'], syl, l['text']))
    print('\n%d줄 · 총 %d음절 · 마지막 종료 %.1fs' % (len(LINES), tot, LINES[-1]['start']+LINES[-1]['limit']))
