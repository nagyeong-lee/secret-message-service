/**
 * anti-capture.js
 * ----------------------------------------------------------------------
 * 비밀 메시지 화면 캡처 방지 다층 방어 로직
 *
 * 적용 위치: api/static/js/anti-capture.js
 * 사용 방법: view_message.html 에서 <script src="{% static 'js/anti-capture.js' %}"></script> 로 로드.
 * 보호 대상: data-secret="true" 속성을 가진 요소 (예: 메시지 박스)
 *
 * ※ 이 스크립트는 일반적인 캡처 시도를 어렵게 만들 뿐,
 *    물리 카메라 촬영이나 OS 레벨 스크린샷을 완벽히 차단하지는 못합니다.
 * ----------------------------------------------------------------------
 */
(function () {
  'use strict';

  // 보호 대상 요소들과 메시지 영역 본체
  const protectedEls = document.querySelectorAll('[data-secret="true"]');
  const messageBox = document.querySelector('.message-box');
  if (protectedEls.length === 0) return;

  // ================================================================
  // [Layer 0] 보호 상태 표시 / 해제 함수
  // ----------------------------------------------------------------
  // 위험 이벤트가 발생하면 메시지를 즉시 가리고, 안전해지면 다시 보임.
  // ================================================================
  let blurOverlay = null;

  function createOverlay(reason) {
    if (blurOverlay) return;
    blurOverlay = document.createElement('div');
    blurOverlay.className = 'capture-shield';
    blurOverlay.innerHTML = `
      <div class="shield-icon">🛡️</div>
      <p class="shield-title">화면이 가려졌습니다</p>
      <p class="shield-reason">${reason}</p>
      <p class="shield-hint">메시지 창으로 돌아오면 다시 표시됩니다</p>
    `;
    document.body.appendChild(blurOverlay);
  }

  function removeOverlay() {
    if (blurOverlay) {
      blurOverlay.remove();
      blurOverlay = null;
    }
  }

  function hideSecret(reason = '캡처 시도가 감지되어 메시지가 일시적으로 차단되었습니다') {
    protectedEls.forEach(el => el.classList.add('secret-hidden'));
    createOverlay(reason);
  }

  function showSecret() {
    protectedEls.forEach(el => el.classList.remove('secret-hidden'));
    removeOverlay();
  }

  // ================================================================
  // [Layer 1] 우클릭(컨텍스트 메뉴) 차단
  // ----------------------------------------------------------------
  // 이미지 저장, "다른 이름으로 저장" 등을 메뉴 단계에서 차단.
  // ================================================================
  document.addEventListener('contextmenu', e => {
    e.preventDefault();
    return false;
  });

  // ================================================================
  // [Layer 2] 텍스트 선택 / 드래그 / 복사 차단
  // ----------------------------------------------------------------
  // CSS의 user-select:none 으로 1차 차단,
  // selectstart / copy / cut 이벤트 차단으로 2차 차단.
  // ================================================================
  document.addEventListener('selectstart', e => {
    if (e.target.closest('[data-secret="true"]')) {
      e.preventDefault();
      return false;
    }
  });
  document.addEventListener('copy', e => {
    e.preventDefault();
    if (e.clipboardData) e.clipboardData.setData('text/plain', '');
  });
  document.addEventListener('cut', e => e.preventDefault());
  document.addEventListener('dragstart', e => e.preventDefault());

  // ================================================================
  // [Layer 3] 위험 단축키 차단
  // ----------------------------------------------------------------
  // PrintScreen / F12 / Ctrl+S / Ctrl+P / Ctrl+U /
  // Ctrl+Shift+I,J,C / Ctrl+A 등을 차단.
  // ================================================================
  document.addEventListener('keydown', e => {
    const key = (e.key || '').toLowerCase();

    // PrintScreen 키
    if (key === 'printscreen' || e.keyCode === 44) {
      // 클립보드를 즉시 비워 캡처된 이미지가 붙여넣어지지 않게 함
      // (브라우저 권한 정책으로 항상 동작하지는 않음)
      try {
        navigator.clipboard.writeText('').catch(() => {});
      } catch (err) {}
      hideSecret('Print Screen 키가 눌렸습니다');
      setTimeout(showSecret, 2000);
      e.preventDefault();
      return false;
    }

    // F12 (개발자 도구)
    if (e.keyCode === 123 || key === 'f12') {
      e.preventDefault();
      return false;
    }

    // Ctrl(⌘) + 단축키
    if (e.ctrlKey || e.metaKey) {
      // Ctrl+S(저장), Ctrl+P(인쇄), Ctrl+U(소스 보기), Ctrl+A(전체 선택)
      if (['s', 'p', 'u', 'a'].includes(key)) {
        e.preventDefault();
        return false;
      }
      // Ctrl+Shift+I / J / C (개발자 도구)
      if (e.shiftKey && ['i', 'j', 'c'].includes(key)) {
        e.preventDefault();
        return false;
      }
    }
  });

  // ================================================================
  // [Layer 4] 페이지 가시성 변화 감지
  // ----------------------------------------------------------------
  // 탭이 백그라운드로 가거나 (Alt+Tab),
  // Win+Shift+S 같은 캡처 도구가 활성화되면 visibilitychange 이벤트 발생.
  // ================================================================
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      hideSecret('탭이 비활성화되었습니다');
    } else {
      showSecret();
    }
  });

  // ================================================================
  // [Layer 5] 윈도우 포커스 변화 감지
  // ----------------------------------------------------------------
  // 다른 창으로 전환될 때(예: 캡처 프로그램 호출) 메시지를 가림.
  // ================================================================
  window.addEventListener('blur', () => hideSecret('창의 포커스가 사라졌습니다'));
  window.addEventListener('focus', () => showSecret());

  // ================================================================
  // [Layer 6] 마우스 포인터 이탈 감지
  // ----------------------------------------------------------------
  // 마우스가 브라우저 영역을 벗어나면 캡처 도구를 호출했을 가능성.
  // (선택적 - 너무 민감하게 동작할 수 있어 일정 시간 후 복구)
  // ================================================================
  document.addEventListener('mouseleave', () => {
    hideSecret('포인터가 영역을 벗어났습니다');
  });
  document.addEventListener('mouseenter', () => showSecret());

  // ================================================================
  // [Layer 7] 개발자 도구 감지
  // ----------------------------------------------------------------
  // outerWidth - innerWidth 차이로 DevTools 도킹 여부 추정.
  // 완벽하지는 않지만 흔한 감지 트릭.
  // ================================================================
  let devtoolsOpen = false;
  setInterval(() => {
    const wDiff = window.outerWidth - window.innerWidth;
    const hDiff = window.outerHeight - window.innerHeight;
    const opened = wDiff > 200 || hDiff > 200;

    if (opened && !devtoolsOpen) {
      devtoolsOpen = true;
      hideSecret('개발자 도구가 감지되었습니다');
    } else if (!opened && devtoolsOpen) {
      devtoolsOpen = false;
      showSecret();
    }
  }, 1000);

  // ================================================================
  // [Layer 8] 인쇄 프리뷰 차단
  // ----------------------------------------------------------------
  // beforeprint 이벤트 발생 시 메시지를 가리고, afterprint 후 복원.
  // (CSS @media print 와 함께 동작)
  // ================================================================
  window.addEventListener('beforeprint', () => hideSecret('인쇄가 시도되었습니다'));
  window.addEventListener('afterprint', () => showSecret());

  // ================================================================
  // [Layer 9] 모바일 캡처 방어 보조
  // ----------------------------------------------------------------
  // 모바일 운영체제 스크린샷은 JS로 막을 수 없지만,
  // pagehide / pageshow 이벤트로 캡처 직후 화면 전환을 감지하기도 함.
  // ================================================================
  window.addEventListener('pagehide', () => hideSecret('페이지가 일시 숨겨졌습니다'));
  window.addEventListener('pageshow', () => showSecret());

  // ================================================================
  // [Layer 10] iframe 임베드 차단 (clickjacking 방지)
  // ----------------------------------------------------------------
  // 다른 사이트에서 이 페이지를 iframe 으로 끼워넣어 캡처하는 시도 차단.
  // (서버에서 X-Frame-Options 헤더를 함께 설정해야 완벽)
  // ================================================================
  if (window.top !== window.self) {
    document.body.innerHTML = '<h2 style="color:#ff7675;text-align:center;padding:60px;">⚠️ 외부 사이트에서의 표시는 허용되지 않습니다.</h2>';
    return;
  }

})();
