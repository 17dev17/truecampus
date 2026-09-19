
const I18N_STORAGE_KEY = 'tc_language';

const translations = {
    ru: {
        app_name: "TrueCampus",
        app_badge: "Global AI",
        slogan_title: "TrueCampus — выбери свою жизнь с умом",
        slogan_subtitle: "Интеллектуальная платформа независимой верификации кампусов университетов со всего мира. Реальные фотографии, честная оценка инфраструктуры и защита от ложных ожиданий.",

        nav_home: "Главное меню",
        nav_audit: "Поиск и аудит",
        nav_compare: "Сравнить",
        nav_about: "О сервисе",
        nav_login_register: "Вход / Регистрация",
        nav_history: "История проверок",
        nav_topup: "Пополнить кредиты",
        nav_logout: "Выйти",

        hero_tag: "AI Верификация кампусов 2026",
        showcase_title: "Популярные университеты мира и Казахстана",
        showcase_subtitle: "Исследуйте проверенные фотостудии, общежития, библиотеки и учебные корпуса перед поступлением",
        btn_explore_campus: "Исследовать кампус",
        btn_start_audit: "Начать проверку университета",
        btn_go_to_search: "Перейти к поиску",
        stat_universities: "1,500+ кампусов в базе",
        stat_categories: "8 зон студенческой жизни",
        stat_accuracy: "99.4% точность отсева фейков",

        auth_required_title: "Требуется регистрация",
        auth_required_desc: "Для запуска анализа университетов и просмотра полной базы верифицированных снимков необходимо войти или зарегистрироваться.",
        auth_free_credits_hint: "🎁 Каждому новому пользователю дарим 5 бесплатных кредитов на проверки!",

        search_hero_title: "Проверенный визуальный профиль кампуса",
        search_hero_subtitle: "Быстрый сервис проверки общежитий, аудиторий, библиотек и студенческой среды с отсевом рекламных рендеров.",
        search_placeholder: "Введите название университета (например: КазНУ, Назарбаев Университет, МГУ, MIT)...",
        search_btn: "Анализировать",
        frequently_searched: "Часто ищут:",

        credits_count: "{n} кредитов",
        credits_cost_notice: "1 проверка = 1 кредит",
        credits_depleted_title: "Кредиты закончились!",
        credits_depleted_desc: "У вас закончился баланс кредитов для анализа кампусов. Пополните счет или активируйте промокод, чтобы продолжить исследования!",
        btn_topup_balance: "Пополнить баланс",
        modal_topup_title: "Пополнение баланса кредитов",
        pkg_starter_title: "Стартовый",
        pkg_starter_desc: "5 проверок кампусов",
        pkg_pro_title: "Студент Pro",
        pkg_pro_desc: "15 проверок + детальный PDF отчет",
        pkg_explorer_title: "Исследователь",
        pkg_explorer_desc: "50 проверок + сравнение без ограничений",
        promo_title: "Есть промокод?",
        promo_placeholder: "Введите промокод (например: CAMPUS2026)",
        promo_apply_btn: "Применить",
        promo_hint: "Используйте промокоды: CAMPUS2026, STUDENT или LOCUS для бесплатных кредитов.",

        modal_auth_login_title: "Вход в личный кабинет",
        modal_auth_reg_title: "Регистрация в TrueCampus",
        tab_login: "Вход",
        tab_register: "Регистрация",
        label_name: "Ваше имя или никнейм",
        placeholder_name: "Алишер",
        label_email: "Email адрес",
        label_password: "Пароль",
        btn_login_submit: "Войти в аккаунт",
        btn_register_submit: "Зарегистрироваться и получить 5 кредитов",

        cat_dormitory: "Общежития и проживание",
        cat_library: "Библиотеки и коворкинги",
        cat_sports: "Спорт и фитнес",
        cat_dining: "Столовые и кафетерии",
        cat_classrooms: "Учебные корпуса и лектории",
        cat_laboratory: "Лаборатории и оборудование",
        cat_campus_grounds: "Территория и парки кампуса",
        cat_student_spaces: "Зоны отдыха студентов",

        step_1: "Поиск университета и локации",
        step_2: "Сбор открытых фото и данных",
        step_3: "Удаление дубликатов (pHash)",
        step_4: "AI-анализ фото и распределение по зонам",
        step_5: "Формирование отчета о кампусе",

        btn_close: "Закрыть",
        btn_understood: "Понятно",
        loading: "Загрузка...",
        verified_badge: "ВЕРИФИЦИРОВАНО",
        unverified_badge: "НЕТ ПОДТВЕРЖДЕННЫХ ФОТО",
        toast_login_success: "Добро пожаловать в TrueCampus!",
        toast_logout: "Вы вышли из системы",
        toast_credit_deducted: "Списан 1 кредит на анализ кампуса"
    },

    en: {
        app_name: "TrueCampus",
        app_badge: "Global AI",
        slogan_title: "TrueCampus — Choose your life wisely",
        slogan_subtitle: "AI verification engine for university visual campuses & student life worldwide. Real unedited photos, authentic infrastructure assessment, and protection from false expectations.",

        nav_home: "Main Menu",
        nav_audit: "Search & Audit",
        nav_compare: "Compare",
        nav_about: "About",
        nav_login_register: "Sign In / Register",
        nav_history: "Audit History",
        nav_topup: "Top Up Credits",
        nav_logout: "Sign Out",

        hero_tag: "AI Campus Verification 2026",
        showcase_title: "Popular Global & Kazakhstan Universities",
        showcase_subtitle: "Explore verified study rooms, dorms, libraries, and facilities before making your life choice",
        btn_explore_campus: "Explore Campus",
        btn_start_audit: "Start University Audit",
        btn_go_to_search: "Go to Search",
        stat_universities: "1,500+ Campuses Listed",
        stat_categories: "8 Student Life Zones",
        stat_accuracy: "99.4% Fake Media Filter",

        auth_required_title: "Registration Required",
        auth_required_desc: "To analyze universities and access full verified campus profiles, please sign in or create an account.",
        auth_free_credits_hint: "🎁 Every new user receives 5 free credits for campus audits!",

        search_hero_title: "Verified Visual Profile of Campus",
        search_hero_subtitle: "Fast inspection of dormitories, classrooms, libraries, and student life with AI noise filtering.",
        search_placeholder: "Enter university name (e.g., Harvard, MIT, KazNU, Oxford)...",
        search_btn: "Analyze",
        frequently_searched: "Popular searches:",

        credits_count: "{n} credits",
        credits_cost_notice: "1 audit = 1 credit",
        credits_depleted_title: "Credits Depleted!",
        credits_depleted_desc: "You have run out of credits for campus analyses. Top up your balance or enter a promo code to continue exploring!",
        btn_topup_balance: "Top Up Balance",
        modal_topup_title: "Top Up Credit Balance",
        pkg_starter_title: "Starter",
        pkg_starter_desc: "5 Campus Audits",
        pkg_pro_title: "Student Pro",
        pkg_pro_desc: "15 Audits + Detailed PDF Report",
        pkg_explorer_title: "Campus Explorer",
        pkg_explorer_desc: "50 Audits + Unlimited Comparisons",
        promo_title: "Have a promo code?",
        promo_placeholder: "Enter promo code (e.g., CAMPUS2026)",
        promo_apply_btn: "Apply",
        promo_hint: "Use promo codes: CAMPUS2026, STUDENT, or LOCUS for free credits.",

        modal_auth_login_title: "Sign In to Account",
        modal_auth_reg_title: "Register for TrueCampus",
        tab_login: "Sign In",
        tab_register: "Register",
        label_name: "Your Name or Nickname",
        placeholder_name: "Alex",
        label_email: "Email Address",
        label_password: "Password",
        btn_login_submit: "Sign In",
        btn_register_submit: "Register & Get 5 Credits",

        cat_dormitory: "Dormitories & Housing",
        cat_library: "Libraries & Coworking",
        cat_sports: "Sports & Athletics",
        cat_dining: "Dining Halls & Cafeterias",
        cat_classrooms: "Classrooms & Lecture Halls",
        cat_laboratory: "Laboratories & Research",
        cat_campus_grounds: "Campus Grounds & Parks",
        cat_student_spaces: "Student Common Areas",

        step_1: "University & Location Lookup",
        step_2: "Aggregating Open Media & Data",
        step_3: "Deduplication via pHash",
        step_4: "AI Zero-shot Categorization & Trust",
        step_5: "Generating Visual Campus Report",

        btn_close: "Close",
        btn_understood: "Understood",
        loading: "Loading...",
        verified_badge: "VERIFIED",
        unverified_badge: "NO VERIFIED MEDIA",
        toast_login_success: "Welcome to TrueCampus!",
        toast_logout: "Signed out successfully",
        toast_credit_deducted: "1 credit deducted for campus audit"
    },

    kz: {
        app_name: "TrueCampus",
        app_badge: "Global AI",
        slogan_title: "TrueCampus — өміріңді ақылмен таңда",
        slogan_subtitle: "Әлемдік университеттердің нақты кампусы мен студенттік өмірін тәуелсіз AI арқылы тексеру платформасы. Шынайы фотосуреттер, инфрақұрылымның әділ бағасы және жалған жарнамадан қорғау.",

        nav_home: "Басты мәзір",
        nav_audit: "Іздеу және аудит",
        nav_compare: "Салыстыру",
        nav_about: "Сервис жайлы",
        nav_login_register: "Кіру / Тіркелу",
        nav_history: "Тексеру тарихы",
        nav_topup: "Кредит толтыру",
        nav_logout: "Шығу",

        hero_tag: "AI Кампусты Тексеру 2026",
        showcase_title: "Әлемнің және Қазақстанның үздік университеттері",
        showcase_subtitle: "Оқуға түспес бұрын нақты жатақханаларды, кітапханаларды және оқу корпустарын зерттеңіз",
        btn_explore_campus: "Кампусты зерттеу",
        btn_start_audit: "Университетті тексеруді бастау",
        btn_go_to_search: "Іздеуге өту",
        stat_universities: "Қорда 1,500+ кампус",
        stat_categories: "Студенттік өмірдің 8 аймағы",
        stat_accuracy: "99.4% сенімділік сүзгісі",

        auth_required_title: "Тіркелу қажет",
        auth_required_desc: "Университеттерді тексеру және расталған фотосуреттерді толық көру үшін тіркелу немесе жүйеге кіру қажет.",
        auth_free_credits_hint: "🎁 Әрбір жаңа пайдаланушыға тексеруге 5 тегін кредит сыйға беріледі!",

        search_hero_title: "Кампустың тексерілген визуалды профилі",
        search_hero_subtitle: "Жатақханаларды, аудиторияларды, кітапханаларды және студенттік ортаны жасанды интеллектпен жылдам тексеру.",
        search_placeholder: "Университет атауын енгізіңіз (мысалы: ҚазҰУ, Назарбаев Университеті, МГУ, MIT)...",
        search_btn: "Талдау",
        frequently_searched: "Жиі ізделетіндер:",

        credits_count: "{n} кредит",
        credits_cost_notice: "1 тексеру = 1 кредит",
        credits_depleted_title: "Кредиттеріңіз таусылды!",
        credits_depleted_desc: "Кампустарды тексеру үшін балансыңыз бітті. Зерттеуді жалғастыру үшін теңгерімді толтырыңыз немесе промокодты пайдаланыңыз!",
        btn_topup_balance: "Теңгерімді толтыру",
        modal_topup_title: "Кредит балансын толтыру",
        pkg_starter_title: "Бастапқы",
        pkg_starter_desc: "5 кампусты тексеру",
        pkg_pro_title: "Студент Pro",
        pkg_pro_desc: "15 тексеру + толық PDF есеп",
        pkg_explorer_title: "Зерттеуші",
        pkg_explorer_desc: "50 тексеру + шектеусіз салыстыру",
        promo_title: "Промокод бар ма?",
        promo_placeholder: "Промокодты енгізіңіз (мысалы: CAMPUS2026)",
        promo_apply_btn: "Қолдану",
        promo_hint: "Тегін кредиттер үшін: CAMPUS2026, STUDENT немесе LOCUS кодтарын қолданыңыз.",

        modal_auth_login_title: "Жеке кабинетке кіру",
        modal_auth_reg_title: "TrueCampus жүйесіне тіркелу",
        tab_login: "Кіру",
        tab_register: "Тіркелу",
        label_name: "Атыңыз немесе бүркеншік есіміңіз",
        placeholder_name: "Әлішер",
        label_email: "Email поштасы",
        label_password: "Құпиясөз",
        btn_login_submit: "Жүйеге кіру",
        btn_register_submit: "Тіркелу және 5 кредит алу",

        cat_dormitory: "Жатақханалар мен тұрғын жай",
        cat_library: "Кітапханалар мен коворкингтер",
        cat_sports: "Спорт және дене шынықтыру",
        cat_dining: "Асханалар мен дәмханалар",
        cat_classrooms: "Оқу ғимараттары мен дәрісханалар",
        cat_laboratory: "Зертханалар мен жабдықтар",
        cat_campus_grounds: "Кампус аумағы мен саябақтар",
        cat_student_spaces: "Студенттердің демалыс орындары",

        step_1: "Университет пен мекенжайды анықтау",
        step_2: "Ашық фотолар мен деректерді жинау",
        step_3: "Қайталанған суреттерді жою (pHash)",
        step_4: "AI фотоларды 8 аймаққа бөлу & Сенімділік",
        step_5: "Кампустың қорытынды есебін құрастыру",

        btn_close: "Жабу",
        btn_understood: "Түсінікті",
        loading: "Жүктелуде...",
        verified_badge: "РАСТАЛҒАН",
        unverified_badge: "РАСТАЛҒАН ДЕРЕК ЖОҚ",
        toast_login_success: "TrueCampus жүйесіне қош келдіңіз!",
        toast_logout: "Жүйеден шықтыңыз",
        toast_credit_deducted: "Кампусты талдауға 1 кредит шегерілді"
    }
};

let currentLanguage = localStorage.getItem(I18N_STORAGE_KEY) || 'ru';

function t(key, params = {}) {
    const dict = translations[currentLanguage] || translations.ru;
    let val = dict[key] || translations.ru[key] || key;
    if (typeof val === 'string' && params) {
        Object.keys(params).forEach(k => {
            val = val.replace(new RegExp(`\\{${k}\\}`, 'g'), params[k]);
        });
    }
    return val;
}

function setLanguage(lang) {
    if (!translations[lang]) lang = 'ru';
    currentLanguage = lang;
    localStorage.setItem(I18N_STORAGE_KEY, lang);
    applyTranslationsToDOM();
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang } }));
}

function getLanguage() {
    return currentLanguage;
}

function applyTranslationsToDOM() {
    document.documentElement.lang = currentLanguage;
    
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const text = t(key);
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
            if (el.getAttribute('placeholder')) {
                el.placeholder = text;
            }
        } else {
            el.textContent = text;
        }
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        el.placeholder = t(key);
    });

    document.querySelectorAll('.lang-btn').forEach(btn => {
        const btnLang = btn.getAttribute('data-lang');
        btn.classList.toggle('active', btnLang === currentLanguage);
    });
}

window.tcI18n = {
    t,
    setLanguage,
    getLanguage,
    applyTranslationsToDOM
};
