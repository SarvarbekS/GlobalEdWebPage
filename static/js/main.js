// Navbar toggle
const navToggle = document.getElementById('navToggle');
const mobileMenu = document.getElementById('mobileMenu');
const siteHeader = document.getElementById('siteHeader');

if (navToggle && mobileMenu) {
    navToggle.addEventListener('click', () => {
        mobileMenu.classList.toggle('active');
        const expanded = navToggle.getAttribute('aria-expanded') === 'true';
        navToggle.setAttribute('aria-expanded', String(!expanded));
    });
    mobileMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.remove('active');
            navToggle.setAttribute('aria-expanded', 'false');
        });
    });
}

function updateHeaderOnScroll() {
    if (!siteHeader) return;
    siteHeader.classList.toggle('scrolled', window.scrollY > 16);
}
window.addEventListener('scroll', updateHeaderOnScroll);
window.addEventListener('load', updateHeaderOnScroll);

// Infinite Results Scroll
function initInfiniteResultsScroll() {
    const resultsScroll = document.getElementById('resultsScroll');
    if (!resultsScroll) return;

    const originalItems = Array.from(resultsScroll.querySelectorAll('.result-poster'));
    if (!originalItems.length) return;

    if (!resultsScroll.dataset.cloned) {
        originalItems.forEach(item => {
            const clone = item.cloneNode(true);
            clone.setAttribute('aria-hidden', 'true');
            clone.removeAttribute('tabindex');
            clone.removeAttribute('role');
            resultsScroll.appendChild(clone);
        });
        resultsScroll.dataset.cloned = 'true';
    }

    let animationId;
    let position = 0;
    const speed = 0.4;

    function getTrackWidth() {
        const gap = parseFloat(window.getComputedStyle(resultsScroll).gap) || 0;
        return originalItems.reduce((total, item, i) => {
            return total + item.offsetWidth + (i < originalItems.length - 1 ? gap : 0);
        }, 0);
    }

    function startAnimation() {
        const resetPoint = getTrackWidth();
        function step() {
            position += speed;
            if (position >= resetPoint) position = 0;
            resultsScroll.style.transform = `translate3d(-${position}px, 0, 0)`;
            animationId = requestAnimationFrame(step);
        }
        if (animationId) cancelAnimationFrame(animationId);
        animationId = requestAnimationFrame(step);
    }

    startAnimation();

    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            position = 0;
            resultsScroll.style.transform = 'translate3d(0, 0, 0)';
            startAnimation();
        }, 150);
    });
}

// Results Modal
function initResultsModal() {
    const overlay  = document.getElementById('resultModal');
    const closeBtn = document.getElementById('modalClose');
    if (!overlay) return;

    const modalImage       = document.getElementById('modalImage');
    const modalName        = document.getElementById('modalName');
    const modalCountryText = document.getElementById('modalCountryText');
    const modalUniversity  = document.getElementById('modalUniversity');
    const modalDescription = document.getElementById('modalDescription');

    function openModal(el) {
        const d = el.dataset;
        modalName.textContent        = d.name        || '';
        modalCountryText.textContent = d.country      || '';
        modalUniversity.textContent  = d.university   || '';
        modalDescription.textContent = d.description  || '';
        modalImage.src = d.image || '';
        modalImage.alt = d.name  || '';
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Use delegation on the scroll container — catches both originals and clones
    const scroll = document.getElementById('resultsScroll');
    if (scroll) {
        scroll.addEventListener('click', e => {
            const card = e.target.closest('.result-poster[data-name]');
            // Only open if it's an original (has tabindex) — ignore aria-hidden clones
            if (card && card.getAttribute('aria-hidden') !== 'true') {
                openModal(card);
            }
        });

        scroll.addEventListener('keydown', e => {
            if (e.key === 'Enter' || e.key === ' ') {
                const card = e.target.closest('.result-poster[data-name]');
                if (card && card.getAttribute('aria-hidden') !== 'true') {
                    e.preventDefault();
                    openModal(card);
                }
            }
        });
    }

    closeBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', e => { if (e.target === overlay) closeModal(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
}

function initHeroTextRotation() {
    const track = document.getElementById('heroRotationTrack');
    if (!track) return;

    const rotationTexts = [
        "100% scholarship in Korea",
        "$6000 scholarship in London",
        "Fully funded scholarship in Italy",
        "Top universities in Seoul",
        "Affordable tuition in Europe",
        "Scholarships in Australia",
        "Study and work in New Zealand"
    ];

    let activeIndex = 0;
    const offsets = [-2, -1, 0, 1, 2];

    function wrap(index) {
        return (index % rotationTexts.length + rotationTexts.length) % rotationTexts.length;
    }

    function render() {
        track.innerHTML = "";

        offsets.forEach(offset => {
            const item = document.createElement("div");
            item.className = "hero-rotation-item";

            if (offset === 0) item.classList.add("is-active");
            if (Math.abs(offset) === 1) item.classList.add("is-near");

            item.textContent = rotationTexts[wrap(activeIndex + offset)];
            track.appendChild(item);
        });
    }

    render();

    setInterval(() => {
        activeIndex = wrap(activeIndex + 1);
        render();
    }, 1000);
}

function initContactRoleSwitcher() {
    const form = document.getElementById('contactForm');
    if (!form) return;

    const roleCards = document.querySelectorAll('.contact-role-card');
    const senderType = document.getElementById('senderType');
    const studentFields = document.querySelectorAll('.student-only-field');
    const partnerFields = document.querySelectorAll('.partner-only-field');
    const formTitle = document.getElementById('contactFormTitle');
    const formIntro = document.getElementById('contactFormIntro');
    const submitText = document.getElementById('contactSubmitText');

    const studentCountry = document.getElementById('country_interest');
    const partnerInstitution = document.getElementById('institution_name');
    const organizationType = document.getElementById('organization_type');
    const partnerCountry = document.getElementById('partner_country');

    function toggleRequired(el, isRequired) {
        if (!el) return;
        el.required = isRequired;
    }

    function setRole(role) {
        senderType.value = role;

        roleCards.forEach(card => {
            card.classList.toggle('active', card.dataset.role === role);
        });

        const isStudent = role === 'student';

        studentFields.forEach(el => {
            el.style.display = isStudent ? '' : 'none';
        });

        partnerFields.forEach(el => {
            el.style.display = isStudent ? 'none' : '';
        });

        if (formTitle) {
            formTitle.textContent = isStudent
                ? 'Start your journey with a conversation.'
                : 'Start a partnership conversation.';
        }

        if (formIntro) {
            formIntro.textContent = isStudent
                ? 'Choose the type of inquiry below and fill in the matching form.'
                : 'Tell us about your institution and partnership goals, and our team will respond shortly.';
        }

        if (submitText) {
            submitText.textContent = isStudent ? 'Send inquiry' : 'Send partnership inquiry';
        }

        toggleRequired(studentCountry, isStudent);
        toggleRequired(partnerInstitution, !isStudent);
        toggleRequired(organizationType, !isStudent);
        toggleRequired(partnerCountry, !isStudent);
    }

    roleCards.forEach(card => {
        card.addEventListener('click', () => setRole(card.dataset.role));
    });

    const initialRole = senderType.value === 'partner' ? 'partner' : 'student';
    setRole(initialRole);
}

function initOpportunitiesWheel() {
    const track = document.getElementById('opportunitiesWheelTrack');
    if (!track) return;

    const items = [
        "Top universities in Seoul",
        "Affordable tuition in Europe",
        "Scholarships in Australia",
        "Study and work in New Zealand",
        "100% scholarship in Korea",
        "$6000 scholarship in London",
        "Fully funded scholarship in Italy"
    ];

    let activeIndex = 0;
    const offsets = [-1, 0, 1];

    function wrap(index) {
        return (index % items.length + items.length) % items.length;
    }

    function render() {
        track.innerHTML = "";

        offsets.forEach(offset => {
            const el = document.createElement("div");
            el.className = "opportunity-wheel-item";

            if (offset === 0) el.classList.add("is-active");
            if (Math.abs(offset) === 1) el.classList.add("is-near");

            const text = document.createElement("span");
            text.textContent = items[wrap(activeIndex + offset)];
            el.appendChild(text);

            track.appendChild(el);
        });
    }

    render();

    setInterval(() => {
        activeIndex = wrap(activeIndex + 1);
        render();
    }, 1800);
}

function initNewsModal() {
    const overlay = document.getElementById('newsModal');
    if (!overlay) return;

    const closeBtn = document.getElementById('newsModalClose');
    const titleEl = document.getElementById('newsModalTitle');
    const dateEl = document.getElementById('newsModalDate');
    const sourceEl = document.getElementById('newsModalSource');
    const bodyEl = document.getElementById('newsModalBody');
    const imageWrap = document.getElementById('newsModalImageWrap');
    const imageEl = document.getElementById('newsModalImage');
    const cards = document.querySelectorAll('.news-card');

    if (!cards.length) return;

    function openModal(card) {
        const d = card.dataset;
        titleEl.textContent = d.title || '';
        dateEl.textContent = d.date || '';
        sourceEl.textContent = d.source ? `· ${d.source}` : '';
        bodyEl.innerHTML = d.body || '';

        if (d.image) {
            imageEl.src = d.image;
            imageEl.alt = d.title || '';
            imageWrap.style.display = '';
        } else {
            imageEl.src = '';
            imageEl.alt = '';
            imageWrap.style.display = 'none';
        }

        overlay.classList.add('active');
        overlay.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        overlay.classList.remove('active');
        overlay.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    cards.forEach(card => {
        card.addEventListener('click', () => openModal(card));
        card.addEventListener('keydown', e => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openModal(card);
            }
        });
    });

    closeBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', e => {
        if (e.target === overlay) closeModal();
    });
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && overlay.classList.contains('active')) closeModal();
    });
}

function initEventModal() {
    const overlay = document.getElementById('eventModal');
    if (!overlay) return;

    const closeBtn = document.getElementById('eventModalClose');
    const titleEl = document.getElementById('eventModalTitle');
    const subtitleEl = document.getElementById('eventModalSubtitle');
    const dateEl = document.getElementById('eventModalDate');
    const locationEl = document.getElementById('eventModalLocation');
    const bodyEl = document.getElementById('eventModalBody');
    const imgWrap = document.getElementById('eventModalImageWrap');
    const imgEl = document.getElementById('eventModalImage');

    const cards = document.querySelectorAll('.event-card');
    if (!cards.length) return;

    function openModal(card) {
        const d = card.dataset;
        titleEl.textContent = d.title || '';
        subtitleEl.textContent = d.subtitle || '';
        subtitleEl.style.display = d.subtitle ? '' : 'none';
        dateEl.textContent = d.date || '';
        locationEl.textContent = d.location ? `· ${d.location}` : '';
        bodyEl.innerHTML = d.body || '';

        if (d.image) {
            imgEl.src = d.image;
            imgEl.alt = d.title || '';
            imgWrap.style.display = '';
        } else {
            imgEl.src = '';
            imgEl.alt = '';
            imgWrap.style.display = 'none';
        }

        overlay.classList.add('active');
        overlay.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        overlay.classList.remove('active');
        overlay.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    cards.forEach(card => {
        card.addEventListener('click', () => openModal(card));
        card.addEventListener('keydown', e => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openModal(card);
            }
        });
    });

    closeBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', e => {
        if (e.target === overlay) closeModal();
    });
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && overlay.classList.contains('active')) {
            closeModal();
        }
    });
}

window.addEventListener('load', () => {
    initInfiniteResultsScroll();
    initResultsModal();
    initHeroTextRotation();
    initContactRoleSwitcher();
    initOpportunitiesWheel();
    initNewsModal && initNewsModal();
    initEventModal && initEventModal();
});