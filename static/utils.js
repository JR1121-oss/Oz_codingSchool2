/**
 * 유틸리티 함수 모음
 */

const utils = {
    showAlert(message, type = 'info', title = '알림') {
        const modal = document.getElementById('alert-modal');
        const iconEl = document.getElementById('alert-modal-icon');
        const titleEl = document.getElementById('alert-modal-title');
        const messageEl = document.getElementById('alert-modal-message');
        const closeBtn = document.getElementById('alert-modal-close-btn');

        if (!modal) {
            alert(message);
            return;
        }

        titleEl.innerText = title;
        messageEl.innerText = message;
        
        // 아이콘 설정
        iconEl.className = 'modal-icon ' + type;
        if (type === 'error') iconEl.innerText = '⚠️';
        else if (type === 'success') iconEl.innerText = '✅';
        else iconEl.innerText = 'ℹ️';

        modal.classList.add('show');

        return new Promise((resolve) => {
            closeBtn.onclick = () => {
                modal.classList.remove('show');
                resolve();
            };
            // 모달 바깥 클릭 시 닫기
            modal.onclick = (e) => {
                if (e.target === modal) {
                    modal.classList.remove('show');
                    resolve();
                }
            };
        });
    },
    // 서버는 UTC를 시간대 표시 없이 보내므로 'Z'를 붙여 UTC로 읽게 한다
    formatDate(value) {
        if (!value) return '-';
        const hasTimezone = /Z$|[+-]\d{2}:?\d{2}$/.test(value);
        return new Date(hasTimezone ? value : value + 'Z').toLocaleString('ko-KR');
    },

    formatPhoneNumber(value) {
        if (!value) return value;
        const phoneNumber = value.replace(/[^\d]/g, '');
        const phoneNumberLength = phoneNumber.length;
        if (phoneNumberLength < 4) return phoneNumber;
        if (phoneNumberLength < 8) {
            return `${phoneNumber.slice(0, 3)}-${phoneNumber.slice(3)}`;
        }
        return `${phoneNumber.slice(0, 3)}-${phoneNumber.slice(3, 7)}-${phoneNumber.slice(7, 11)}`;
    },

    formatPhoneNumber(value) {
        if (!value) return value;
        const phoneNumber = value.replace(/[^\d]/g, '');
        const phoneNumberLength = phoneNumber.length;
        if (phoneNumberLength < 4) return phoneNumber;
        if (phoneNumberLength < 8) {
            return `${phoneNumber.slice(0, 3)}-${phoneNumber.slice(3)}`;
        }
        return `${phoneNumber.slice(0, 3)}-${phoneNumber.slice(3, 7)}-${phoneNumber.slice(7, 11)}`;
    },

    handlePhoneInput(e) {
        const formattedValue = this.formatPhoneNumber(e.target.value);
        e.target.value = formattedValue;
    },

    templatesCache: {},

    async loadTemplate(name) {
        if (this.templatesCache[name]) return this.templatesCache[name];
        const response = await fetch(`/static/templates/${name}.html`);
        const html = await response.text();
        this.templatesCache[name] = html;
        return html;
    }
};
