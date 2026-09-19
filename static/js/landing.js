
const POPULAR_UNIVERSITIES = [
    {
        id: "kaznu",
        query: "КазНУ им. Аль-Фараби",
        name_ru: "КазНУ им. Аль-Фараби",
        name_en: "Al-Farabi Kazakh National University",
        name_kz: "Әл-Фараби атындағы ҚазҰУ",
        city_ru: "Алматы, Казахстан",
        city_en: "Almaty, Kazakhstan",
        city_kz: "Алматы, Қазақстан",
        country_group: "kz",
        trust_index: 94,
        zones_count: 8,
        rating: "№1 в Казахстане",
        tags_ru: ["Казгуград", "Общежития", "Спорткомплекс", "Научная библиотека"],
        tags_en: ["Kazgugrad", "Dormitories", "Sports Arena", "Science Library"],
        tags_kz: ["Қазғұқлашығы", "Жатақханалар", "Спорт кешені", "Ғылыми кітапхана"],
        image: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Kazakh_National_University_main_building.jpg/640px-Kazakh_National_University_main_building.jpg",
        description_ru: "Крупнейший студенческий городок Казгуград с 14 общежитиями, стадионом и Дворцом студентов.",
        description_en: "The largest academic campus Kazgugrad with 14 residential dorms, stadium, and Student Palace.",
        description_kz: "14 жатақханасы, стадионы және Студенттер сарайы бар ең үлкен Қазғұқлашығы кампусы."
    },
    {
        id: "nu",
        query: "Назарбаев Университет",
        name_ru: "Назарбаев Университет (NU)",
        name_en: "Nazarbayev University",
        name_kz: "Назарбаев Университеті",
        city_ru: "Астана, Казахстан",
        city_en: "Astana, Kazakhstan",
        city_kz: "Астана, Қазақстан",
        country_group: "kz",
        trust_index: 98,
        zones_count: 8,
        rating: "Международный кампус",
        tags_ru: ["Крытый атриум", "Апарт-общежития", "Робототехника", "Фитнес-центр"],
        tags_en: ["Indoor Atrium", "Modern Dorms", "Robotics Labs", "Fitness Center"],
        tags_kz: ["Жабық атриум", "Заманауи жатақхана", "Робототехника", "Фитнес орталығы"],
        image: "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Nazarbayev_University_Main_Atrium.jpg/640px-Nazarbayev_University_Main_Atrium.jpg",
        description_ru: "Современный полностью крытый кампус, соединенный теплыми переходами для суровой астанинской зимы.",
        description_en: "Modern climate-controlled campus connected via indoor skywalks designed for Astana winter.",
        description_kz: "Астананың қысына бейімделген, барлық корпустары жылы өткелдермен жалғанған заманауи кампус."
    },
    {
        id: "satbayev",
        query: "Satbayev University",
        name_ru: "Satbayev University (Политех)",
        name_en: "Satbayev University",
        name_kz: "Сәтбаев Университеті",
        city_ru: "Алматы, Казахстан",
        city_en: "Almaty, Kazakhstan",
        city_kz: "Алматы, Қазақстан",
        country_group: "kz",
        trust_index: 92,
        zones_count: 8,
        rating: "Инженерный флагман",
        tags_ru: ["FabLab", "Центр геологии", "IT-хаб", "Военная кафедра"],
        tags_en: ["FabLab", "Geology Center", "IT Hub", "Engineering Center"],
        tags_kz: ["FabLab", "Геология орталығы", "IT-хаб", "Инженерлік кешен"],
        image: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Satbayev_University_Main_Facade.jpg/640px-Satbayev_University_Main_Facade.jpg",
        description_ru: "Исторический политехнический вуз в центре Алматы с мощными инженерными лабораториями.",
        description_en: "Historic polytechnic campus in central Almaty with advanced engineering and robotics facilities.",
        description_kz: "Алматының орталығында орналасқан тарихи политехникалық жетекші инженерлік оқу орны."
    },
    {
        id: "kbtu",
        query: "КБТУ",
        name_ru: "Казахстанско-Британский Технический Университет",
        name_en: "Kazakh-British Technical University (KBTU)",
        name_kz: "Қазақстан-Британ Техникалық Университеті",
        city_ru: "Алматы, Казахстан",
        city_en: "Almaty, Kazakhstan",
        city_kz: "Алматы, Қазақстан",
        country_group: "kz",
        trust_index: 95,
        zones_count: 8,
        rating: "IT и Нефтегаз",
        tags_ru: ["Историческое здание", "IT лаборатории", "Bloomberg Hall", "Студ-кафе"],
        tags_en: ["Historic Building", "IT Labs", "Bloomberg Hall", "Cafeteria"],
        tags_kz: ["Тарихи ғимарат", "IT зертханалар", "Bloomberg Hall", "Студенттік дәмхана"],
        image: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/KBTU_Almaty_Front.jpg/640px-KBTU_Almaty_Front.jpg",
        description_ru: "Монументальное историческое здание правительства с высокотехнологичными IT-кластерами.",
        description_en: "Grand historic government building equipped with cutting-edge IT and petroleum laboratories.",
        description_kz: "Жоғары технологиялық IT зертханалары бар тарихи монументалды ғимарат."
    },
    {
        id: "mit",
        query: "Massachusetts Institute of Technology",
        name_ru: "Массачусетский Технологический Институт (MIT)",
        name_en: "Massachusetts Institute of Technology (MIT)",
        name_kz: "Массачусетс Технологиялық Институты (MIT)",
        city_ru: "Кембридж, США",
        city_en: "Cambridge, USA",
        city_kz: "Кембридж, АҚШ",
        country_group: "world",
        trust_index: 99,
        zones_count: 8,
        rating: "№1 в мире QS",
        tags_ru: ["Большой купол", "Media Lab", "Simmons Hall", "Стадион Zesiger"],
        tags_en: ["Great Dome", "Media Lab", "Simmons Hall", "Zesiger Center"],
        tags_kz: ["Үлкен күмбез", "Media Lab", "Simmons Hall", "Спорт кешені"],
        image: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/MIT_Building_10_and_the_Great_Dome%2C_Cambridge_MA.jpg/640px-MIT_Building_10_and_the_Great_Dome%2C_Cambridge_MA.jpg",
        description_ru: "Легендарный кампус вдоль реки Чарльз с футуристическими лабораториями и общежитиями.",
        description_en: "Legendary campus along the Charles River featuring futuristic labs and student housing.",
        description_kz: "Чарльз өзенінің жағасында орналасқан әлемнің №1 технологиялық оқу орны."
    },
    {
        id: "oxford",
        query: "University of Oxford",
        name_ru: "Оксфордский Университет",
        name_en: "University of Oxford",
        name_kz: "Оксфорд Университеті",
        city_ru: "Оксфорд, Великобритания",
        city_en: "Oxford, United Kingdom",
        city_kz: "Оксфорд, Ұлыбритания",
        country_group: "world",
        trust_index: 99,
        zones_count: 8,
        rating: "Топ 3 мира",
        tags_ru: ["Бодлианская библиотека", "Christ Church", "Колледжи", "Канал реки"],
        tags_en: ["Bodleian Library", "Christ Church", "Historic Colleges", "Rowing Club"],
        tags_kz: ["Бодлиан кітапханасы", "Christ Church", "Колледждер", "Есу клубы"],
        image: "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Radcliffe_Camera%2C_Oxford_-_Oct_2006.jpg/640px-Radcliffe_Camera%2C_Oxford_-_Oct_2006.jpg",
        description_ru: "Старейший университет англоязычного мира с уникальной системой 39 самоуправляемых колледжей.",
        description_en: "The oldest university in the English-speaking world with 39 picturesque collegiate campuses.",
        description_kz: "39 жеке колледжден құралған ағылшын тілді әлемнің ең көне және беделді университеті."
    },
    {
        id: "harvard",
        query: "Harvard University",
        name_ru: "Гарвардский Университет",
        name_en: "Harvard University",
        name_kz: "Гарвард Университеті",
        city_ru: "Кембридж / Бостон, США",
        city_en: "Cambridge / Boston, USA",
        city_kz: "Кембридж / Бостон, АҚШ",
        country_group: "world",
        trust_index: 97,
        zones_count: 8,
        rating: "Лига Плюща",
        tags_ru: ["Гарвард-Ярд", "Widener Library", "Статуя Джона Гарварда", "Студ-город"],
        tags_en: ["Harvard Yard", "Widener Library", "John Harvard Statue", "Residential Houses"],
        tags_kz: ["Гарвард-Ярд", "Widener кітапханасы", "Тарихи кампус", "Жатақханалар"],
        image: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Harvard_Yard_in_autumn.jpg/640px-Harvard_Yard_in_autumn.jpg",
        description_ru: "Сердце Лиги Плюща с живописным кампусом Гарвард-Ярд и богатейшей университетской библиотекой.",
        description_en: "The heart of Ivy League featuring historic Harvard Yard and the world-renowned Widener Library.",
        description_kz: "Әлемге әйгілі Гарвард-Ярд кампусы мен ең бай университет кітапханасы бар білім ордасы."
    },
    {
        id: "msu",
        query: "МГУ имени М.В. Ломоносова",
        name_ru: "МГУ имени М.В. Ломоносова",
        name_en: "Lomonosov Moscow State University",
        name_kz: "М.В. Ломоносов атындағы ММУ",
        city_ru: "Москва",
        city_en: "Moscow",
        city_kz: "Мәскеу",
        country_group: "world",
        trust_index: 93,
        zones_count: 8,
        rating: "Главный вуз СНГ",
        tags_ru: ["Главное Здание", "Дом Студента (ДАС)", "Ботанический сад", "Бассейн"],
        tags_en: ["Main Tower", "Student Dorms", "Botanical Garden", "Olympic Pool"],
        tags_kz: ["Бас ғимарат", "Студенттер үйі", "Ботаникалық бақ", "Бассейн"],
        image: "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Main_building_of_Moscow_State_University_facing_SW.jpg/640px-Main_building_of_Moscow_State_University_facing_SW.jpg",
        description_ru: "Знаменитая высотка на Воробьёвых горах, где учебные аудитории и общежития находятся под одной крышей.",
        description_en: "Iconic skyscraper on Sparrow Hills where classrooms, dormitories, and facilities reside under one roof.",
        description_kz: "Оқу аудиториялары мен студенттік жатақханалары бір шаңырақ астында орналасқан атақты зәулім кешен."
    }
];

let activeFilter = 'all';

function renderUniversityCards() {
    const grid = document.getElementById('universityShowcaseGrid');
    if (!grid) return;

    const lang = window.tcI18n ? window.tcI18n.getLanguage() : 'ru';
    const exploreText = window.tcI18n ? window.tcI18n.t('btn_explore_campus') : 'Исследовать кампус';

    const filtered = POPULAR_UNIVERSITIES.filter(u => {
        if (activeFilter === 'kz') return u.country_group === 'kz';
        if (activeFilter === 'world') return u.country_group === 'world';
        return true;
    });

    grid.innerHTML = filtered.map(u => {
        const name = u[`name_${lang}`] || u.name_ru;
        const city = u[`city_${lang}`] || u.city_ru;
        const desc = u[`description_${lang}`] || u.description_ru;
        const tags = u[`tags_${lang}`] || u.tags_ru;

        return `
            <div class="univ-card" data-query="${escapeHtml(u.query)}">
                <div class="univ-card-img-wrap">
                    <img src="${u.image}" alt="${escapeHtml(name)}" loading="lazy" onerror="this.onerror=null;this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22640%22 height=%22360%22 fill=%22%230f172a%22%3E%3Crect width=%22640%22 height=%22360%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22%2364748b%22 font-size=%2220%22 font-family=%22sans-serif%22%3E🏛️ Campus Photo%3C/text%3E%3C/svg%3E'" />
                    <div class="univ-card-badge-rating">${escapeHtml(u.rating)}</div>
                    <div class="univ-card-trust-pill">
                        <span class="trust-dot"></span>
                        <span>${u.trust_index}% Trust</span>
                    </div>
                </div>
                <div class="univ-card-body">
                    <div class="univ-card-location">📍 ${escapeHtml(city)}</div>
                    <h3 class="univ-card-title">${escapeHtml(name)}</h3>
                    <p class="univ-card-desc">${escapeHtml(desc)}</p>
                    <div class="univ-card-tags">
                        ${tags.map(t => `<span class="univ-tag">${escapeHtml(t)}</span>`).join('')}
                    </div>
                </div>
                <div class="univ-card-footer">
                    <div class="univ-card-zones">
                        <span class="zones-icon">🏛️</span>
                        <span>${u.zones_count} ${lang === 'en' ? 'zones' : (lang === 'kz' ? 'аймақ' : 'зон кампуса')}</span>
                    </div>
                    <button type="button" class="btn-explore-univ" data-univ-query="${escapeHtml(u.query)}">
                        <span>${exploreText}</span>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                            <polyline points="12 5 19 12 12 19"></polyline>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    }).join('');

    grid.querySelectorAll('.btn-explore-univ, .univ-card').forEach(el => {
        el.addEventListener('click', (e) => {
            const q = el.getAttribute('data-univ-query') || el.getAttribute('data-query');
            if (q) {
                if (el.classList.contains('univ-card') && e.target.closest('.btn-explore-univ')) {
                    return;
                }
                handleExploreUniversity(q);
            }
        });
    });
}

function handleExploreUniversity(query) {
    if (!window.tcAuth || !window.tcAuth.isAuthenticated()) {
        window.tcAuth.requireAuth(() => {
            handleExploreUniversity(query);
        }, window.tcI18n ? window.tcI18n.t('auth_required_desc') : 'Для анализа университета необходимо войти или зарегистрироваться.');
        return;
    }

    if (window.tcCredits && window.tcCredits.getBalance() <= 0) {
        window.tcCredits.openTopUpModal(window.tcI18n ? window.tcI18n.t('credits_depleted_desc') : 'Кредиты закончились! Пожалуйста, пополните баланс.');
        return;
    }

    if (window.tcApp) {
        window.tcApp.switchToAuditView(query);
    }
}

function initLanding() {
    renderUniversityCards();

    document.querySelectorAll('.filter-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            activeFilter = pill.getAttribute('data-filter') || 'all';
            renderUniversityCards();
        });
    });

    window.addEventListener('languageChanged', () => {
        renderUniversityCards();
    });

    const btnStartAudit = document.getElementById('heroBtnStartAudit');
    const btnGoToSearch = document.getElementById('heroBtnGoToSearch');

    if (btnStartAudit) {
        btnStartAudit.addEventListener('click', () => {
            if (!window.tcAuth.isAuthenticated()) {
                window.tcAuth.requireAuth(() => {
                    if (window.tcApp) window.tcApp.switchToAuditView();
                });
            } else {
                if (window.tcApp) window.tcApp.switchToAuditView();
            }
        });
    }

    if (btnGoToSearch) {
        btnGoToSearch.addEventListener('click', () => {
            if (window.tcApp) window.tcApp.switchToAuditView();
        });
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.toString().replace(/[&<>"']/g, m => map[m]);
}

window.tcLanding = {
    renderUniversityCards,
    handleExploreUniversity,
    initLanding
};
