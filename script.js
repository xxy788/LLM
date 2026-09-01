/* 天气出行助手 - 核心 JS */
const CONFIG = {
    WEATHER_API_KEY: 'c66cc1485a864469ab633416262906',
    WEATHER_API_BASE: 'https://api.weatherapi.com/v1',
    AI_API_URL: 'https://text.pollinations.ai/openai/v1/chat/completions',
    AI_MODEL: 'openai',
    DEFAULT_CITY: '北京',
    MAX_HISTORY: 10,
    MAX_FAVORITES: 10,
    DEBOUNCE_MS: 350,
};

/* 国家 → 国旗 Emoji */
const COUNTRY_FLAG_MAP = {
    'China': '🇨🇳', '中国': '🇨🇳',
    'Japan': '🇯🇵', '日本': '🇯🇵',
    'South Korea': '🇰🇷', '韩国': '🇰🇷', 'Korea': '🇰🇷',
    'North Korea': '🇰🇵', '朝鲜': '🇰🇵',
    'Mongolia': '🇲🇳', '蒙古': '🇲🇳',
    'India': '🇮🇳', '印度': '🇮🇳',
    'Thailand': '🇹🇭', '泰国': '🇹🇭',
    'Vietnam': '🇻🇳', '越南': '🇻🇳',
    'Malaysia': '🇲🇾', '马来西亚': '🇲🇾',
    'Singapore': '🇸🇬', '新加坡': '🇸🇬',
    'Indonesia': '🇮🇩', '印度尼西亚': '🇮🇩',
    'Philippines': '🇵🇭', '菲律宾': '🇵🇭',
    'Myanmar': '🇲🇲', '缅甸': '🇲🇲', 'Burma': '🇲🇲',
    'Cambodia': '🇰🇭', '柬埔寨': '🇰🇭',
    'Laos': '🇱🇦', '老挝': '🇱🇦',
    'Nepal': '🇳🇵', '尼泊尔': '🇳🇵',
    'Bhutan': '🇧🇹', '不丹': '🇧🇹',
    'Bangladesh': '🇧🇩', '孟加拉国': '🇧🇩',
    'Sri Lanka': '🇱🇰', '斯里兰卡': '🇱🇰',
    'Maldives': '🇲🇻', '马尔代夫': '🇲🇻',
    'Pakistan': '🇵🇰', '巴基斯坦': '🇵🇰',
    'Afghanistan': '🇦🇫', '阿富汗': '🇦🇫',
    'Kazakhstan': '🇰🇿', '哈萨克斯坦': '🇰🇿',
    'Uzbekistan': '🇺🇿', '乌兹别克斯坦': '🇺🇿',
    'Turkmenistan': '🇹🇲', '土库曼斯坦': '🇹🇲',
    'Kyrgyzstan': '🇰🇬', '吉尔吉斯斯坦': '🇰🇬',
    'Tajikistan': '🇹🇯', '塔吉克斯坦': '🇹🇯',
    'United Arab Emirates': '🇦🇪', '阿联酋': '🇦🇪', 'UAE': '🇦🇪',
    'Saudi Arabia': '🇸🇦', '沙特阿拉伯': '🇸🇦', '沙特': '🇸🇦',
    'Qatar': '🇶🇦', '卡塔尔': '🇶🇦',
    'Kuwait': '🇰🇼', '科威特': '🇰🇼',
    'Bahrain': '🇧🇭', '巴林': '🇧🇭',
    'Oman': '🇴🇲', '阿曼': '🇴🇲',
    'Yemen': '🇾🇪', '也门': '🇾🇪',
    'Jordan': '🇯🇴', '约旦': '🇯🇴',
    'Lebanon': '🇱🇧', '黎巴嫩': '🇱🇧',
    'Syria': '🇸🇾', '叙利亚': '🇸🇾',
    'Iraq': '🇮🇶', '伊拉克': '🇮🇶',
    'Iran': '🇮🇷', '伊朗': '🇮🇷',
    'Turkey': '🇹🇷', '土耳其': '🇹🇷', 'Turkiye': '🇹🇷',
    'Israel': '🇮🇱', '以色列': '🇮🇱',
    'Palestine': '🇵🇸', '巴勒斯坦': '🇵🇸',
    'Georgia': '🇬🇪', '格鲁吉亚': '🇬🇪',
    'Armenia': '🇦🇲', '亚美尼亚': '🇦🇲',
    'Azerbaijan': '🇦🇿', '阿塞拜疆': '🇦🇿',
    'Taiwan': '🇨🇳', '台湾': '🇨🇳',
    'Hong Kong': '🇨🇳', '香港': '🇨🇳', 'Hong Kong SAR': '🇨🇳',
    'Macau': '🇨🇳', '澳门': '🇨🇳', 'Macao': '🇨🇳',
    'United Kingdom': '🇬🇧', '英国': '🇬🇧', 'UK': '🇬🇧',
    'France': '🇫🇷', '法国': '🇫🇷',
    'Germany': '🇩🇪', '德国': '🇩🇪',
    'Italy': '🇮🇹', '意大利': '🇮🇹',
    'Spain': '🇪🇸', '西班牙': '🇪🇸',
    'Portugal': '🇵🇹', '葡萄牙': '🇵🇹',
    'Netherlands': '🇳🇱', '荷兰': '🇳🇱',
    'Belgium': '🇧🇪', '比利时': '🇧🇪',
    'Switzerland': '🇨🇭', '瑞士': '🇨🇭',
    'Austria': '🇦🇹', '奥地利': '🇦🇹',
    'Sweden': '🇸🇪', '瑞典': '🇸🇪',
    'Norway': '🇳🇴', '挪威': '🇳🇴',
    'Denmark': '🇩🇰', '丹麦': '🇩🇰',
    'Finland': '🇫🇮', '芬兰': '🇫🇮',
    'Iceland': '🇮🇸', '冰岛': '🇮🇸',
    'Ireland': '🇮🇪', '爱尔兰': '🇮🇪',
    'Poland': '🇵🇱', '波兰': '🇵🇱',
    'Czech Republic': '🇨🇿', '捷克': '🇨🇿', 'Czechia': '🇨🇿',
    'Slovakia': '🇸🇰', '斯洛伐克': '🇸🇰',
    'Hungary': '🇭🇺', '匈牙利': '🇭🇺',
    'Romania': '🇷🇴', '罗马尼亚': '🇷🇴',
    'Bulgaria': '🇧🇬', '保加利亚': '🇧🇬',
    'Greece': '🇬🇷', '希腊': '🇬🇷',
    'Ukraine': '🇺🇦', '乌克兰': '🇺🇦',
    'Belarus': '🇧🇾', '白俄罗斯': '🇧🇾',
    'Russia': '🇷🇺', '俄罗斯': '🇷🇺',
    'Croatia': '🇭🇷', '克罗地亚': '🇭🇷',
    'Serbia': '🇷🇸', '塞尔维亚': '🇷🇸',
    'Slovenia': '🇸🇮', '斯洛文尼亚': '🇸🇮',
    'Estonia': '🇪🇪', '爱沙尼亚': '🇪🇪',
    'Latvia': '🇱🇻', '拉脱维亚': '🇱🇻',
    'Lithuania': '🇱🇹', '立陶宛': '🇱🇹',
    'Luxembourg': '🇱🇺', '卢森堡': '🇱🇺',
    'Monaco': '🇲🇨', '摩纳哥': '🇲🇨',
    'Malta': '🇲🇹', '马耳他': '🇲🇹',
    'Cyprus': '🇨🇾', '塞浦路斯': '🇨🇾',
    'Albania': '🇦🇱', '阿尔巴尼亚': '🇦🇱',
    'Andorra': '🇦🇩', '安道尔': '🇦🇩',
    'Bosnia and Herzegovina': '🇧🇦', '波黑': '🇧🇦',
    'Liechtenstein': '🇱🇮', '列支敦士登': '🇱🇮',
    'Moldova': '🇲🇩', '摩尔多瓦': '🇲🇩',
    'Montenegro': '🇲🇪', '黑山': '🇲🇪',
    'North Macedonia': '🇲🇰', '北马其顿': '🇲🇰',
    'San Marino': '🇸🇲', '圣马力诺': '🇸🇲',
    'Vatican City': '🇻🇦', '梵蒂冈': '🇻🇦',
    'United States of America': '🇺🇸', '美国': '🇺🇸', 'USA': '🇺🇸', 'United States': '🇺🇸',
    'Canada': '🇨🇦', '加拿大': '🇨🇦',
    'Mexico': '🇲🇽', '墨西哥': '🇲🇽',
    'Cuba': '🇨🇺', '古巴': '🇨🇺',
    'Jamaica': '🇯🇲', '牙买加': '🇯🇲',
    'Bahamas': '🇧🇸', '巴哈马': '🇧🇸',
    'Dominican Republic': '🇩🇴', '多米尼加': '🇩🇴',
    'Guatemala': '🇬🇹', '危地马拉': '🇬🇹',
    'Costa Rica': '🇨🇷', '哥斯达黎加': '🇨🇷',
    'Panama': '🇵🇦', '巴拿马': '🇵🇦',
    'Honduras': '🇭🇳', '洪都拉斯': '🇭🇳',
    'El Salvador': '🇸🇻', '萨尔瓦多': '🇸🇻',
    'Nicaragua': '🇳🇮', '尼加拉瓜': '🇳🇮',
    'Belize': '🇧🇿', '伯利兹': '🇧🇿',
    'Haiti': '🇭🇹', '海地': '🇭🇹',
    'Puerto Rico': '🇵🇷', '波多黎各': '🇵🇷',
    'Greenland': '🇬🇱', '格陵兰': '🇬🇱',
    'Brazil': '🇧🇷', '巴西': '🇧🇷',
    'Argentina': '🇦🇷', '阿根廷': '🇦🇷',
    'Chile': '🇨🇱', '智利': '🇨🇱',
    'Colombia': '🇨🇴', '哥伦比亚': '🇨🇴',
    'Peru': '🇵🇪', '秘鲁': '🇵🇪',
    'Venezuela': '🇻🇪', '委内瑞拉': '🇻🇪',
    'Ecuador': '🇪🇨', '厄瓜多尔': '🇪🇨',
    'Bolivia': '🇧🇴', '玻利维亚': '🇧🇴',
    'Uruguay': '🇺🇾', '乌拉圭': '🇺🇾',
    'Paraguay': '🇵🇾', '巴拉圭': '🇵🇾',
    'Guyana': '🇬🇾', '圭亚那': '🇬🇾',
    'Suriname': '🇸🇷', '苏里南': '🇸🇷',
    'Egypt': '🇪🇬', '埃及': '🇪🇬',
    'South Africa': '🇿🇦', '南非': '🇿🇦',
    'Nigeria': '🇳🇬', '尼日利亚': '🇳🇬',
    'Kenya': '🇰🇪', '肯尼亚': '🇰🇪',
    'Ethiopia': '🇪🇹', '埃塞俄比亚': '🇪🇹',
    'Morocco': '🇲🇦', '摩洛哥': '🇲🇦',
    'Tanzania': '🇹🇿', '坦桑尼亚': '🇹🇿',
    'Ghana': '🇬🇭', '加纳': '🇬🇭',
    'Algeria': '🇩🇿', '阿尔及利亚': '🇩🇿',
    'Tunisia': '🇹🇳', '突尼斯': '🇹🇳',
    'Libya': '🇱🇾', '利比亚': '🇱🇾',
    'Sudan': '🇸🇩', '苏丹': '🇸🇩',
    'Uganda': '🇺🇬', '乌干达': '🇺🇬',
    'Senegal': '🇸🇳', '塞内加尔': '🇸🇳',
    'Zimbabwe': '🇿🇼', '津巴布韦': '🇿🇼',
    'Botswana': '🇧🇼', '博茨瓦纳': '🇧🇼',
    'Mauritius': '🇲🇺', '毛里求斯': '🇲🇺',
    'Madagascar': '🇲🇬', '马达加斯加': '🇲🇬',
    'Angola': '🇦🇴', '安哥拉': '🇦🇴',
    'Cameroon': '🇨🇲', '喀麦隆': '🇨🇲',
    'Ivory Coast': '🇨🇮', '科特迪瓦': '🇨🇮', "Côte d'Ivoire": '🇨🇮',
    'Rwanda': '🇷🇼', '卢旺达': '🇷🇼',
    'Seychelles': '🇸🇨', '塞舌尔': '🇸🇨',
    'Namibia': '🇳🇦', '纳米比亚': '🇳🇦',
    'Zambia': '🇿🇲', '赞比亚': '🇿🇲',
    'Mozambique': '🇲🇿', '莫桑比克': '🇲🇿',
    'Congo': '🇨🇬', '刚果': '🇨🇬',
    'Australia': '🇦🇺', '澳大利亚': '🇦🇺',
    'New Zealand': '🇳🇿', '新西兰': '🇳🇿',
    'Fiji': '🇫🇯', '斐济': '🇫🇯',
    'Papua New Guinea': '🇵🇬', '巴布亚新几内亚': '🇵🇬',
    'Solomon Islands': '🇸🇧', '所罗门群岛': '🇸🇧',
    'Vanuatu': '🇻🇺', '瓦努阿图': '🇻🇺',
    'Samoa': '🇼🇸', '萨摩亚': '🇼🇸',
    'Tonga': '🇹🇴', '汤加': '🇹🇴',
    'England': '🇬🇧', 'Scotland': '🇬🇧', 'Wales': '🇬🇧', 'Northern Ireland': '🇬🇧',
    'Catalonia': '🇪🇸', 'Sicily': '🇮🇹', 'Hawaii': '🇺🇸', 'Alaska': '🇺🇸', 'California': '🇺🇸',
};

function getCountryFlag(countryName) {
    if (!countryName) return '🌍';
    if (COUNTRY_FLAG_MAP[countryName]) return COUNTRY_FLAG_MAP[countryName];
    for (const [key, flag] of Object.entries(COUNTRY_FLAG_MAP)) {
        if (countryName.includes(key) || key.includes(countryName)) return flag;
    }
    const upper = countryName.toUpperCase();
    const isoFlags = {
        'CN': '🇨🇳', 'US': '🇺🇸', 'JP': '🇯🇵', 'KR': '🇰🇷', 'GB': '🇬🇧',
        'FR': '🇫🇷', 'DE': '🇩🇪', 'IT': '🇮🇹', 'ES': '🇪🇸', 'RU': '🇷🇺',
        'CA': '🇨🇦', 'AU': '🇦🇺', 'BR': '🇧🇷', 'IN': '🇮🇳', 'SG': '🇸🇬',
        'TH': '🇹🇭', 'VN': '🇻🇳', 'MY': '🇲🇾', 'PH': '🇵🇭', 'ID': '🇮🇩',
        'MX': '🇲🇽', 'AR': '🇦🇷', 'CL': '🇨🇱', 'CO': '🇨🇴', 'PE': '🇵🇪',
        'ZA': '🇿🇦', 'EG': '🇪🇬', 'NG': '🇳🇬', 'KE': '🇰🇪', 'MA': '🇲🇦',
        'AE': '🇦🇪', 'SA': '🇸🇦', 'QA': '🇶🇦', 'TR': '🇹🇷', 'GR': '🇬🇷',
        'PT': '🇵🇹', 'NL': '🇳🇱', 'BE': '🇧🇪', 'CH': '🇨🇭', 'AT': '🇦🇹',
        'SE': '🇸🇪', 'NO': '🇳🇴', 'DK': '🇩🇰', 'FI': '🇫🇮', 'IE': '🇮🇪',
        'PL': '🇵🇱', 'CZ': '🇨🇿', 'HU': '🇭🇺', 'RO': '🇷🇴', 'UA': '🇺🇦',
        'NZ': '🇳🇿', 'HK': '🇨🇳', 'TW': '🇨🇳', 'MO': '🇨🇳',
    };
    if (isoFlags[upper]) return isoFlags[upper];
    return '🌍';
}

/* 国家名 → 中文全名 */
const COUNTRY_CN_MAP = {
    'CN': '中国', 'US': '美国', 'USA': '美国', 'JP': '日本', 'JPN': '日本',
    'KR': '韩国', 'KOR': '韩国', 'KP': '朝鲜', 'PRK': '朝鲜',
    'GB': '英国', 'UK': '英国', 'GBR': '英国', 'ENG': '英国',
    'FR': '法国', 'FRA': '法国', 'DE': '德国', 'DEU': '德国',
    'IT': '意大利', 'ITA': '意大利', 'ES': '西班牙', 'ESP': '西班牙',
    'RU': '俄罗斯', 'RUS': '俄罗斯', 'CA': '加拿大', 'CAN': '加拿大',
    'AU': '澳大利亚', 'AUS': '澳大利亚', 'BR': '巴西', 'BRA': '巴西',
    'IN': '印度', 'IND': '印度', 'SG': '新加坡', 'SGP': '新加坡',
    'TH': '泰国', 'THA': '泰国', 'VN': '越南', 'VNM': '越南',
    'MY': '马来西亚', 'MYS': '马来西亚', 'PH': '菲律宾', 'PHL': '菲律宾',
    'ID': '印度尼西亚', 'IDN': '印度尼西亚', 'MX': '墨西哥', 'MEX': '墨西哥',
    'AR': '阿根廷', 'ARG': '阿根廷', 'CL': '智利', 'CHL': '智利',
    'CO': '哥伦比亚', 'COL': '哥伦比亚', 'PE': '秘鲁', 'PER': '秘鲁',
    'ZA': '南非', 'ZAF': '南非', 'EG': '埃及', 'EGY': '埃及',
    'NG': '尼日利亚', 'NGA': '尼日利亚', 'KE': '肯尼亚', 'KEN': '肯尼亚',
    'MA': '摩洛哥', 'MAR': '摩洛哥', 'AE': '阿联酋', 'ARE': '阿联酋', 'UAE': '阿联酋',
    'SA': '沙特阿拉伯', 'SAU': '沙特阿拉伯', 'QA': '卡塔尔', 'QAT': '卡塔尔',
    'TR': '土耳其', 'TUR': '土耳其', 'GR': '希腊', 'GRC': '希腊',
    'PT': '葡萄牙', 'PRT': '葡萄牙', 'NL': '荷兰', 'NLD': '荷兰',
    'BE': '比利时', 'BEL': '比利时', 'CH': '瑞士', 'CHE': '瑞士',
    'AT': '奥地利', 'AUT': '奥地利', 'SE': '瑞典', 'SWE': '瑞典',
    'NO': '挪威', 'NOR': '挪威', 'DK': '丹麦', 'DNK': '丹麦',
    'FI': '芬兰', 'FIN': '芬兰', 'IE': '爱尔兰', 'IRL': '爱尔兰',
    'PL': '波兰', 'POL': '波兰', 'CZ': '捷克', 'CZE': '捷克',
    'HU': '匈牙利', 'HUN': '匈牙利', 'RO': '罗马尼亚', 'ROU': '罗马尼亚',
    'UA': '乌克兰', 'UKR': '乌克兰', 'NZ': '新西兰', 'NZL': '新西兰',
    'HK': '中国香港', 'HKG': '中国香港', 'TW': '中国台湾', 'TWN': '中国台湾',
    'MO': '中国澳门', 'MAC': '中国澳门', 'PK': '巴基斯坦', 'PAK': '巴基斯坦',
    'BD': '孟加拉国', 'BGD': '孟加拉国', 'NP': '尼泊尔', 'NPL': '尼泊尔',
    'LK': '斯里兰卡', 'LKA': '斯里兰卡', 'MM': '缅甸', 'MMR': '缅甸',
    'KH': '柬埔寨', 'KHM': '柬埔寨', 'LA': '老挝', 'LAO': '老挝',
    'MN': '蒙古', 'MNG': '蒙古', 'IR': '伊朗', 'IRN': '伊朗',
    'IQ': '伊拉克', 'IRQ': '伊拉克', 'SY': '叙利亚', 'SYR': '叙利亚',
    'JO': '约旦', 'JOR': '约旦', 'LB': '黎巴嫩', 'LBN': '黎巴嫩',
    'IL': '以色列', 'ISR': '以色列', 'PS': '巴勒斯坦', 'PSE': '巴勒斯坦',
    'YE': '也门', 'YEM': '也门', 'OM': '阿曼', 'OMN': '阿曼',
    'BH': '巴林', 'BHR': '巴林', 'KW': '科威特', 'KWT': '科威特',
    'KZ': '哈萨克斯坦', 'KAZ': '哈萨克斯坦', 'UZ': '乌兹别克斯坦', 'UZB': '乌兹别克斯坦',
    'TM': '土库曼斯坦', 'TKM': '土库曼斯坦', 'KG': '吉尔吉斯斯坦', 'KGZ': '吉尔吉斯斯坦',
    'TJ': '塔吉克斯坦', 'TJK': '塔吉克斯坦', 'AZ': '阿塞拜疆', 'AZE': '阿塞拜疆',
    'GE': '格鲁吉亚', 'GEO': '格鲁吉亚', 'AM': '亚美尼亚', 'ARM': '亚美尼亚',
    'CY': '塞浦路斯', 'CYP': '塞浦路斯', 'IS': '冰岛', 'ISL': '冰岛',
    'LU': '卢森堡', 'LUX': '卢森堡', 'MC': '摩纳哥', 'MCO': '摩纳哥',
    'LI': '列支敦士登', 'LIE': '列支敦士登', 'AD': '安道尔', 'AND': '安道尔',
    'SM': '圣马力诺', 'SMR': '圣马力诺', 'VA': '梵蒂冈', 'VAT': '梵蒂冈',
    'AL': '阿尔巴尼亚', 'ALB': '阿尔巴尼亚', 'BA': '波黑', 'BIH': '波黑',
    'BG': '保加利亚', 'BGR': '保加利亚', 'HR': '克罗地亚', 'HRV': '克罗地亚',
    'SI': '斯洛文尼亚', 'SVN': '斯洛文尼亚', 'SK': '斯洛伐克', 'SVK': '斯洛伐克',
    'EE': '爱沙尼亚', 'EST': '爱沙尼亚', 'LV': '拉脱维亚', 'LVA': '拉脱维亚',
    'LT': '立陶宛', 'LTU': '立陶宛', 'BY': '白俄罗斯', 'BLR': '白俄罗斯',
    'MD': '摩尔多瓦', 'MDA': '摩尔多瓦', 'RS': '塞尔维亚', 'SRB': '塞尔维亚',
    'ME': '黑山', 'MNE': '黑山', 'MK': '北马其顿', 'MKD': '北马其顿',
    'CU': '古巴', 'CUB': '古巴', 'JM': '牙买加', 'JAM': '牙买加',
    'DO': '多米尼加', 'DOM': '多米尼加', 'GT': '危地马拉', 'GTM': '危地马拉',
    'CR': '哥斯达黎加', 'CRI': '哥斯达黎加', 'PA': '巴拿马', 'PAN': '巴拿马',
    'EC': '厄瓜多尔', 'ECU': '厄瓜多尔', 'VE': '委内瑞拉', 'VEN': '委内瑞拉',
    'BO': '玻利维亚', 'BOL': '玻利维亚', 'PY': '巴拉圭', 'PRY': '巴拉圭',
    'UY': '乌拉圭', 'URY': '乌拉圭', 'DZ': '阿尔及利亚', 'DZA': '阿尔及利亚',
    'TN': '突尼斯', 'TUN': '突尼斯', 'LY': '利比亚', 'LBY': '利比亚',
    'SD': '苏丹', 'SDN': '苏丹', 'ET': '埃塞俄比亚', 'ETH': '埃塞俄比亚',
    'TZ': '坦桑尼亚', 'TZA': '坦桑尼亚', 'UG': '乌干达', 'UGA': '乌干达',
    'RW': '卢旺达', 'RWA': '卢旺达', 'GH': '加纳', 'GHA': '加纳',
    'SN': '塞内加尔', 'SEN': '塞内加尔', 'CM': '喀麦隆', 'CMR': '喀麦隆',
    'AO': '安哥拉', 'AGO': '安哥拉', 'ZM': '赞比亚', 'ZMB': '赞比亚',
    'ZW': '津巴布韦', 'ZWE': '津巴布韦', 'BW': '博茨瓦纳', 'BWA': '博茨瓦纳',
    'MZ': '莫桑比克', 'MOZ': '莫桑比克', 'MG': '马达加斯加', 'MDG': '马达加斯加',
    'MU': '毛里求斯', 'MUS': '毛里求斯', 'SC': '塞舌尔', 'SYC': '塞舌尔',
    'NA': '纳米比亚', 'NAM': '纳米比亚', 'FJ': '斐济', 'FJI': '斐济',
    'PG': '巴布亚新几内亚', 'PNG': '巴布亚新几内亚', 'MV': '马尔代夫', 'MDV': '马尔代夫',
    'BS': '巴哈马', 'BHS': '巴哈马', 'BZ': '伯利兹', 'BLZ': '伯利兹',
    'HT': '海地', 'HTI': '海地', 'PR': '波多黎各', 'PRI': '波多黎各',
    'SV': '萨尔瓦多', 'SLV': '萨尔瓦多', 'HN': '洪都拉斯', 'HND': '洪都拉斯',
    'NI': '尼加拉瓜', 'NIC': '尼加拉瓜', 'GY': '圭亚那', 'GUY': '圭亚那',
    'SR': '苏里南', 'SUR': '苏里南', 'GL': '格陵兰', 'GRL': '格陵兰',
    'SB': '所罗门群岛', 'SLB': '所罗门群岛', 'VU': '瓦努阿图', 'VUT': '瓦努阿图',
    'WS': '萨摩亚', 'WSM': '萨摩亚', 'TO': '汤加', 'TON': '汤加',
    'CD': '刚果民主共和国', 'COD': '刚果民主共和国', 'CG': '刚果', 'COG': '刚果',
    'CI': '科特迪瓦', 'CIV': '科特迪瓦', 'AF': '阿富汗', 'AFG': '阿富汗',
    'China': '中国', 'Japan': '日本', 'South Korea': '韩国', 'Korea': '韩国',
    'North Korea': '朝鲜', 'United States': '美国', 'United States of America': '美国',
    'United Kingdom': '英国', 'France': '法国', 'Germany': '德国',
    'Italy': '意大利', 'Spain': '西班牙', 'Russia': '俄罗斯',
    'Canada': '加拿大', 'Australia': '澳大利亚', 'Brazil': '巴西',
    'India': '印度', 'Singapore': '新加坡', 'Thailand': '泰国',
    'Vietnam': '越南', 'Malaysia': '马来西亚', 'Philippines': '菲律宾',
    'Indonesia': '印度尼西亚', 'Mexico': '墨西哥', 'Argentina': '阿根廷',
    'Chile': '智利', 'Colombia': '哥伦比亚', 'Peru': '秘鲁',
    'South Africa': '南非', 'Egypt': '埃及', 'Nigeria': '尼日利亚',
    'Kenya': '肯尼亚', 'Morocco': '摩洛哥', 'United Arab Emirates': '阿联酋',
    'Saudi Arabia': '沙特阿拉伯', 'Qatar': '卡塔尔', 'Turkey': '土耳其',
    'Greece': '希腊', 'Portugal': '葡萄牙', 'Netherlands': '荷兰',
    'Belgium': '比利时', 'Switzerland': '瑞士', 'Austria': '奥地利',
    'Sweden': '瑞典', 'Norway': '挪威', 'Denmark': '丹麦',
    'Finland': '芬兰', 'Ireland': '爱尔兰', 'Poland': '波兰',
    'Czech Republic': '捷克', 'Czechia': '捷克', 'Hungary': '匈牙利',
    'Romania': '罗马尼亚', 'Ukraine': '乌克兰', 'New Zealand': '新西兰',
    'Hong Kong': '中国香港', 'Hong Kong SAR': '中国香港',
    'Taiwan': '中国台湾', 'Macau': '中国澳门', 'Macao': '中国澳门',
    'Pakistan': '巴基斯坦', 'Bangladesh': '孟加拉国', 'Nepal': '尼泊尔',
    'Sri Lanka': '斯里兰卡', 'Myanmar': '缅甸', 'Burma': '缅甸',
    'Cambodia': '柬埔寨', 'Laos': '老挝', 'Mongolia': '蒙古',
    'Iran': '伊朗', 'Iraq': '伊拉克', 'Syria': '叙利亚',
    'Jordan': '约旦', 'Lebanon': '黎巴嫩', 'Israel': '以色列',
    'Palestine': '巴勒斯坦', 'Yemen': '也门', 'Oman': '阿曼',
    'Bahrain': '巴林', 'Kuwait': '科威特', 'Kazakhstan': '哈萨克斯坦',
    'Uzbekistan': '乌兹别克斯坦', 'Turkmenistan': '土库曼斯坦',
    'Kyrgyzstan': '吉尔吉斯斯坦', 'Tajikistan': '塔吉克斯坦',
    'Azerbaijan': '阿塞拜疆', 'Georgia': '格鲁吉亚', 'Armenia': '亚美尼亚',
    'Cyprus': '塞浦路斯', 'Malta': '马耳他', 'Iceland': '冰岛',
    'Luxembourg': '卢森堡', 'Monaco': '摩纳哥', 'San Marino': '圣马力诺',
    'Vatican City': '梵蒂冈', 'Albania': '阿尔巴尼亚', 'Bulgaria': '保加利亚',
    'Croatia': '克罗地亚', 'Slovenia': '斯洛文尼亚', 'Slovakia': '斯洛伐克',
    'Estonia': '爱沙尼亚', 'Latvia': '拉脱维亚', 'Lithuania': '立陶宛',
    'Belarus': '白俄罗斯', 'Moldova': '摩尔多瓦', 'Serbia': '塞尔维亚',
    'Montenegro': '黑山', 'North Macedonia': '北马其顿',
    'Cuba': '古巴', 'Jamaica': '牙买加', 'Dominican Republic': '多米尼加',
    'Guatemala': '危地马拉', 'Costa Rica': '哥斯达黎加', 'Panama': '巴拿马',
    'Ecuador': '厄瓜多尔', 'Venezuela': '委内瑞拉', 'Bolivia': '玻利维亚',
    'Paraguay': '巴拉圭', 'Uruguay': '乌拉圭', 'Algeria': '阿尔及利亚',
    'Tunisia': '突尼斯', 'Libya': '利比亚', 'Sudan': '苏丹',
    'Ethiopia': '埃塞俄比亚', 'Tanzania': '坦桑尼亚', 'Uganda': '乌干达',
    'Rwanda': '卢旺达', 'Ghana': '加纳', 'Senegal': '塞内加尔',
    'Cameroon': '喀麦隆', 'Angola': '安哥拉', 'Zambia': '赞比亚',
    'Zimbabwe': '津巴布韦', 'Botswana': '博茨瓦纳', 'Mozambique': '莫桑比克',
    'Madagascar': '马达加斯加', 'Mauritius': '毛里求斯', 'Seychelles': '塞舌尔',
    'Namibia': '纳米比亚', 'Ivory Coast': '科特迪瓦', "Côte d'Ivoire": '科特迪瓦',
    'Fiji': '斐济', 'Papua New Guinea': '巴布亚新几内亚', 'Maldives': '马尔代夫',
    'Bahamas': '巴哈马', 'Belize': '伯利兹', 'Haiti': '海地', 'Puerto Rico': '波多黎各',
    'El Salvador': '萨尔瓦多', 'Honduras': '洪都拉斯', 'Nicaragua': '尼加拉瓜',
    'Guyana': '圭亚那', 'Suriname': '苏里南', 'Greenland': '格陵兰',
    'Liechtenstein': '列支敦士登', 'Andorra': '安道尔',
    'Bosnia and Herzegovina': '波黑',
    'Solomon Islands': '所罗门群岛', 'Vanuatu': '瓦努阿图',
    'Samoa': '萨摩亚', 'Tonga': '汤加', 'Afghanistan': '阿富汗',
    'England': '英国', 'Scotland': '英国', 'Wales': '英国', 'Northern Ireland': '英国',
};

function getCountryDisplayName(rawCountry) {
    if (!rawCountry) return '';
    const s = rawCountry.trim();
    if (/[一-龥]/.test(s)) return s;
    for (const [key, val] of Object.entries(COUNTRY_CN_MAP)) {
        if (key.toLowerCase() === s.toLowerCase()) return val;
    }
    if (s.length <= 3 && /^[a-zA-Z]+$/.test(s)) return s.toUpperCase();
    return s;
}

/* 全局状态 */
const state = {
    currentPage: 'home',
    currentWeather: null,
    forecast: null,
    currentCity: '',
    currentCountry: '',
    chatHistory: [],
    isLoading: false,
    favorites: [],
    history: [],
};

/* 本地存储 */
function loadFromStorage(key, defaultValue) {
    try { const raw = localStorage.getItem('weather_app_' + key); return raw === null ? defaultValue : JSON.parse(raw); } catch { return defaultValue; }
}
function saveToStorage(key, value) { try { localStorage.setItem('weather_app_' + key, JSON.stringify(value)); } catch {} }
function loadFavorites() { state.favorites = loadFromStorage('favorites', []); }
function saveFavorites() { saveToStorage('favorites', state.favorites); }
function loadHistory() { state.history = loadFromStorage('history', []); }
function saveHistory() { saveToStorage('history', state.history); }

function addToHistory(city, country) {
    state.history = state.history.filter(h => h.city !== city);
    state.history.unshift({ city, country, time: Date.now() });
    if (state.history.length > CONFIG.MAX_HISTORY) state.history = state.history.slice(0, CONFIG.MAX_HISTORY);
    saveHistory(); renderHistoryList();
}

function toggleFavorite(city, country) {
    const idx = state.favorites.findIndex(f => f.city === city);
    if (idx >= 0) { state.favorites.splice(idx, 1); showToast('已取消收藏'); }
    else {
        if (state.favorites.length >= CONFIG.MAX_FAVORITES) { showToast('收藏已达上限'); return false; }
        state.favorites.push({ city, country, time: Date.now() }); showToast('⭐ 已收藏 ' + city);
    }
    saveFavorites(); renderFavoritesList(); return true;
}

function isFavorite(city) { return state.favorites.some(f => f.city === city); }

/* DOM 引用 */
const DOM = (function () {
    const ids = [
        'navTitle', 'navBack', 'navShare', 'navMore',
        'pageHome', 'pageTravel', 'pageChat', 'pageProfile',
        'cityInput', 'searchBtn', 'searchClear',
        'searchPanel', 'panelDomestic', 'panelInternational', 'panelSuggestions',
        'weatherSection', 'currentWeatherCard', 'detailsSection', 'weatherDetailsCard',
        'detailsGrid', 'forecastSection', 'forecastCard', 'forecastContainer',
        'aqiSection', 'aqiContent',
        'travelSection', 'scoreCard', 'clothingSection', 'clothingContent',
        'activitySection', 'activityContent', 'warningSection', 'warningContent',
        'tipsSection', 'tipsContent',
        'chatMessages', 'chatInput', 'sendBtn', 'chatDateLabel',
        'favoritesList', 'historyList',
        'loadingOverlay', 'mpToast',
        'cityDetailPopup', 'cityDetailContent',
        'editFavorites', 'clearHistory',
    ];
    const dom = {};
    ids.forEach(id => { dom[id] = document.getElementById(id); });
    dom.tabBarItems = document.querySelectorAll('.tab-bar-item');
    dom.pageContainer = document.getElementById('pageContainer');
    dom.allPages = document.querySelectorAll('.page');
    return dom;
})();

/* 工具函数 */
function showLoading() { DOM.loadingOverlay.style.display = 'flex'; state.isLoading = true; }
function hideLoading() { DOM.loadingOverlay.style.display = 'none'; state.isLoading = false; }

function showToast(message, icon, duration) {
    duration = duration || 1800;
    const toast = DOM.mpToast;
    toast.querySelector('.mp-toast-icon').textContent = icon || '';
    toast.querySelector('.mp-toast-text').textContent = message;
    toast.style.display = 'flex'; toast.classList.remove('fade-out');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => { toast.classList.add('fade-out'); setTimeout(() => { toast.style.display = 'none'; }, 300); }, duration);
}

function formatFullTime(dateStr) {
    const d = new Date(dateStr);
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}/${pad(d.getMonth()+1)}/${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function getRelativeTime(ts) {
    const diff = Date.now() - ts;
    const min = Math.floor(diff / 60000);
    if (min < 1) return '刚刚';
    if (min < 60) return min + '分钟前';
    if (min < 1440) return Math.floor(min / 60) + '小时前';
    if (min < 10080) return Math.floor(min / 1440) + '天前';
    return formatFullTime(new Date(ts).toISOString());
}

function escapeHtml(text) { const div = document.createElement('div'); div.textContent = text; return div.innerHTML; }

/* 天气图标 */
function getWeatherIcon(code, isDay) {
    isDay = isDay !== false;
    const map = {
        1000: isDay ? '☀️' : '🌙', 1003: isDay ? '🌤️' : '🌤️', 1006: '☁️', 1009: '🌥️',
        1030: '🌁', 1063: '🌦️', 1066: '🌨️', 1069: '🌧️', 1072: '🌧️',
        1087: '⛈️', 1114: '🌬️', 1117: '🌨️', 1135: '🌁', 1147: '🌁',
        1150: '🌦️', 1153: '🌦️', 1168: '🌧️', 1171: '🌧️',
        1180: '🌦️', 1183: '🌧️', 1186: '🌧️', 1189: '🌧️',
        1192: '🌧️', 1195: '🌧️', 1198: '🌧️', 1201: '🌧️',
        1204: '🌧️', 1207: '🌧️',
        1210: '🌨️', 1213: '🌨️', 1216: '🌨️', 1219: '🌨️',
        1222: '❄️', 1225: '❄️', 1237: '🌨️',
        1240: '🌦️', 1243: '🌧️', 1246: '⛈️',
        1249: '🌧️', 1252: '🌧️',
        1255: '🌨️', 1258: '🌨️', 1261: '❄️', 1264: '❄️',
        1273: '⛈️', 1276: '⛈️', 1279: '⛈️', 1282: '⛈️',
    };
    return map[code] || '🌁';
}

/* 天气主题 */
function getWeatherTheme(code, isDay) {
    if (isDay === 0) return 'night';
    if (code === 1000) return 'sunny';
    if (code >= 1003 && code <= 1009) return 'cloudy';
    if ((code >= 1066 && code <= 1069) || (code >= 1114 && code <= 1117) ||
        (code >= 1204 && code <= 1264 && code !== 1240 && code !== 1243 && code !== 1246)) return 'snowy';
    if (code >= 1063 && code <= 1264) return 'rainy';
    if (code >= 1273 && code <= 1282) return 'stormy';
    if (code >= 1030 && code <= 1147) return 'misty';
    return 'default';
}

function applyWeatherTheme(code, isDay) {
    const theme = getWeatherTheme(code, isDay);
    const body = document.body;
    const classList = body.className.split(' ').filter(c => !c.startsWith('theme-'));
    classList.push('theme-' + theme);
    body.className = classList.join(' ');
    if (theme === 'rainy' || theme === 'stormy') startRainDrops(); else stopRainDrops();
}

/* 雨滴系统 */
let rainInterval = null, rainDrops = [];
function startRainDrops() {
    stopRainDrops();
    const container = document.getElementById('wbRain');
    if (!container) return;
    rainInterval = setInterval(function () {
        const count = 10 + Math.floor(Math.random() * 9);
        for (let i = 0; i < count; i++) {
            const drop = document.createElement('div');
            const r = Math.random();
            if (r < 0.4) drop.className = 'wb-drop big';
            else if (r < 0.75) drop.className = 'wb-drop';
            else drop.className = 'wb-drop small';
            drop.style.left = (Math.random() * 98) + '%';
            const duration = 0.4 + Math.random() * 0.8;
            drop.style.animationDuration = duration + 's';
            drop.style.animationDelay = -(Math.random() * duration) + 's';
            container.appendChild(drop); rainDrops.push(drop);
            setTimeout(function () { if (drop.parentNode) { drop.remove(); rainDrops = rainDrops.filter(d => d !== drop); } }, duration * 1000 + 200);
        }
        if (rainDrops.length > 300) { const old = rainDrops.splice(0, 50); old.forEach(d => { if (d.parentNode) d.remove(); }); }
    }, 45);
}
function stopRainDrops() { if (rainInterval) { clearInterval(rainInterval); rainInterval = null; } rainDrops.forEach(d => { if (d.parentNode) d.remove(); }); rainDrops = []; }

/* TabBar 路由 */
function switchPage(pageName, direction) {
    if (state.currentPage === pageName) return;
    const oldPage = document.querySelector('.page.active');
    const newPage = document.getElementById('page' + pageName.charAt(0).toUpperCase() + pageName.slice(1));
    if (!oldPage || !newPage || oldPage === newPage) return;
    direction = direction || 'forward';
    oldPage.classList.remove('active', 'slide-left-enter', 'slide-left-leave', 'slide-right-enter', 'slide-right-leave');
    newPage.classList.remove('active', 'slide-left-enter', 'slide-left-leave', 'slide-right-enter', 'slide-right-leave');
    if (direction === 'forward') { oldPage.classList.add('slide-left-leave'); newPage.classList.add('slide-left-enter'); }
    else { oldPage.classList.add('slide-right-leave'); newPage.classList.add('slide-right-enter'); }
    const onAnimEnd = function(e) { if (e.target !== newPage) return; newPage.removeEventListener('animationend', onAnimEnd); oldPage.classList.remove('active', 'slide-left-leave', 'slide-right-leave'); newPage.classList.remove('slide-left-enter', 'slide-right-enter'); newPage.classList.add('active'); state.currentPage = pageName; };
    newPage.addEventListener('animationend', onAnimEnd);
}

function switchTab(pageName) {
    DOM.tabBarItems.forEach(item => item.classList.toggle('active', item.dataset.page === pageName));
    const titles = { home: '天气出行助手', travel: '出行建议', chat: 'AI 出行问答', profile: '我的' };
    DOM.navTitle.textContent = titles[pageName] || pageName;
    DOM.navBack.style.display = 'none';
    const pageOrder = ['home', 'travel', 'chat', 'profile'];
    const oldIdx = pageOrder.indexOf(state.currentPage), newIdx = pageOrder.indexOf(pageName);
    switchPage(pageName, newIdx > oldIdx ? 'forward' : 'backward');
}

DOM.tabBarItems.forEach(item => item.addEventListener('click', function () { const p = this.dataset.page; if (state.currentPage !== p) switchTab(p); }));

/* WeatherAPI */
async function searchCities(query) {
    if (!query || query.length < 1) { DOM.panelSuggestions.style.display = 'none'; DOM.panelDomestic.style.display = ''; DOM.panelInternational.style.display = 'none'; return; }
    try {
        const resp = await fetch(`${CONFIG.WEATHER_API_BASE}/search.json?key=${CONFIG.WEATHER_API_KEY}&q=${encodeURIComponent(query)}&lang=zh`);
        if (!resp.ok) throw new Error('搜索失败');
        renderSuggestions(await resp.json());
    } catch (err) { console.error(err); }
}

async function fetchCurrentWeather(city) {
    const resp = await fetch(`${CONFIG.WEATHER_API_BASE}/current.json?key=${CONFIG.WEATHER_API_KEY}&q=${encodeURIComponent(city)}&aqi=yes&lang=
    zh`);
    if (!resp.ok) { const err = await resp.json().catch(() => ({})); throw new Error(err.error?.message || '获取失败'); }
    return await resp.json();
}

async function fetchForecast(city) {
    const resp = await fetch(`${CONFIG.WEATHER_API_BASE}/forecast.json?key=${CONFIG.WEATHER_API_KEY}&q=${encodeURIComponent(city)}&days=3&aqi=
    yes&lang=zh`);
    if (!resp.ok) { const err = await resp.json().catch(() => ({})); throw new Error(err.error?.message || '获取失败'); }
    return await resp.json();
}

async function queryWeather(city) {
    showLoading();
    try {
        const [current, forecastData] = await Promise.all([fetchCurrentWeather(city), fetchForecast(city)]);
        state.currentWeather = current; state.forecast = forecastData;
        state.currentCity = current.location.name; state.currentCountry = getCountryDisplayName(current.location.country);
        addToHistory(state.currentCity, state.currentCountry);
        applyWeatherTheme(current.current.condition.code, current.current.is_day);
        renderAllWeatherSections(); renderAllTravelSections();
        ['weatherSection','detailsSection','forecastSection','aqiSection','travelSection','clothingSection','activitySection','warningSection',
            'tipsSection'].forEach(id => DOM[id].style.display = 'block');
        DOM.weatherSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        addWeatherContextToChat(); updateFavoriteButton();
    } catch (err) { showToast(err.message, '⚠️', 2500); } finally { hideLoading(); }
}

/* 搜索建议 */
let debounceTimer = null;
function renderSuggestions(cities) {
    if (!cities || cities.length === 0) { DOM.panelSuggestions.style.display = 'none'; DOM.panelDomestic.style.display = ''; return; }
    DOM.panelDomestic.style.display = 'none'; DOM.panelInternational.style.display = 'none'; DOM.panelSuggestions.style.display = '';
    DOM.panelSuggestions.innerHTML = cities.slice(0, 10).map(city => {
        const flag = getCountryFlag(city.country), country = getCountryDisplayName(city.country || '');
        return `<div class="mp-suggestion-item" data-city="${escapeHtml(city.name)}" data-country="${escapeHtml(country)}">
        <span class="mp-suggestion-flag">${flag}</span><div class="mp-suggestion-info"><div class="mp-suggestion-city">${escapeHtml(city.name)}
        </div><div class="mp-suggestion-detail">${escapeHtml(country)}</div></div></div>`;
    }).join('');
    DOM.panelSuggestions.querySelectorAll('.mp-suggestion-item').forEach(item => item.addEventListener('click', function () 
    { DOM.cityInput.value = this.dataset.city; closeSearchPanel(); DOM.searchClear.style.display = 'flex'; queryWeather(this.dataset.city); }));
}

function closeSearchPanel() { DOM.searchPanel.classList.remove('active'); DOM.panelSuggestions.style.display = 'none';
     DOM.panelSuggestions.innerHTML = ''; DOM.panelDomestic.style.display = ''; DOM.panelInternational.style.display = 'none'; }
function openSearchPanel() { DOM.searchPanel.classList.add('active'); DOM.panelSuggestions.style.display = 'none'; 
    DOM.panelSuggestions.innerHTML = ''; const activeTab = document.querySelector('.mp-panel-tab.active'); 
    const tab = activeTab ? activeTab.dataset.tab : 'domestic'; DOM.panelDomestic.style.display = tab === 'domestic' ? '' : 'none'; 
    DOM.panelInternational.style.display = tab === 'international' ? '' : 'none'; }

/* 面板标签 */
DOM.searchPanel.addEventListener('click', function (e) {
    const tab = e.target.closest('.mp-panel-tab');
    if (tab) { e.stopPropagation(); const tabName = tab.dataset.tab; document.querySelectorAll('.mp-panel-tab').
        forEach(t => t.classList.remove('active')); tab.classList.add('active'); DOM.panelDomestic.style.display = tabName === 'domestic' ? '' : 'none'; DOM.panelInternational.style.display = tabName === 'international' ? '' : 'none'; DOM.panelSuggestions.style.display = 'none'; DOM.panelSuggestions.innerHTML = ''; DOM.cityInput.value = ''; DOM.searchClear.style.display = 'none'; }
});

/* 天气渲染 */
function renderAllWeatherSections() { renderCurrentWeatherCard(); renderDetailsGrid(); renderForecastList(); renderAQI(); }

function renderCurrentWeatherCard() {
    const w = state.currentWeather.current, loc = state.currentWeather.location, isDay = w.is_day === 1;
    const icon = getWeatherIcon(w.condition.code, isDay), flag = getCountryFlag(loc.country);
    const dayData = state.forecast.forecast.forecastday[0].day;
    DOM.currentWeatherCard.innerHTML = `<div class="mp-weather-flag-row"><span class="mp-weather-country-flag">${flag}</span><span class="mp-weather-city-name">${escapeHtml(loc.name)}</span></div><div class="mp-weather-local-time">${getCountryDisplayName(loc.country)} · ${formatFullTime(loc.localtime)}</div><div class="mp-weather-icon-display">${icon}</div><div class="mp-weather-temp-display">${Math.round(w.temp_c)}<span class="unit">°C</span></div><div class="mp-weather-condition-text">${w.condition.text}</div><div class="mp-weather-feels-like">体感温度 ${Math.round(w.feelslike_c)}°C</div><div class="mp-weather-quick-stats"><div class="mp-quick-stat"><div class="mp-quick-stat-value">${Math.round(dayData.maxtemp_c)}°</div><div class="mp-quick-stat-label">最高温</div></div><div class="mp-quick-stat"><div class="mp-quick-stat-value">${Math.round(dayData.mintemp_c)}°</div><div class="mp-quick-stat-label">最低温</div></div><div class="mp-quick-stat"><div class="mp-quick-stat-value">${w.humidity}%</div><div class="mp-quick-stat-label">湿度</div></div><div class="mp-quick-stat"><div class="mp-quick-stat-value">${w.wind_kph}</div><div class="mp-quick-stat-label">风速 km/h</div></div></div>`;
}

/* 风向 → 中文 */
function getWindDirCN(dir) {
    if (!dir) return '—';
    if (/[一-龥]/.test(dir)) return dir;
    const map = {
        'N': '北风', 'NNE': '东北偏北风', 'NE': '东北风', 'ENE': '东北偏东风',
        'E': '东风', 'ESE': '东南偏东风', 'SE': '东南风', 'SSE': '东南偏南风',
        'S': '南风', 'SSW': '西南偏南风', 'SW': '西南风', 'WSW': '西南偏西风',
        'W': '西风', 'WNW': '西北偏西风', 'NW': '西北风', 'NNW': '西北偏北风',
    };
    return map[dir.toUpperCase()] || dir;
}

function renderDetailsGrid() {
    const w = state.currentWeather.current, day = state.forecast.forecast.forecastday[0].day, aqi = w.air_quality || {};
    const cells = [
        { icon: '🌡️', value: `${Math.round(w.feelslike_c)}°C`, label: '体感温度' }, { icon: '💧', value: `${w.humidity}%`, label: '相对湿度' },
        { icon: '💨', value: `${w.wind_kph} 公里/小时`, label: '风速' }, { icon: '🧭', value: getWindDirCN(w.wind_dir), label: '风向' },
        { icon: '🔭', value: `${w.vis_km} 公里`, label: '能见度' }, { icon: '☀️', value: `${day.uv}`, label: '紫外线指数' },
        { icon: '🌧️', value: `${w.precip_mm} 毫米`, label: '降水量' }, { icon: '☁️', value: `${w.cloud}%`, label: '云量' },
        { icon: '🌀', value: `${w.pressure_mb} 百帕`, label: '气压' }, { icon: '🌬️', value: `${w.gust_kph} 公里/小时`, label: '阵风' },
    ];
    if (aqi.pm2_5 !== undefined) cells.push({ icon: '🫁', value: aqi.pm2_5.toFixed(1), label: 'PM2.5' }, { icon: '🌁', value: (aqi.pm10 || 0).toFixed(1), label: 'PM10' }, { icon: '🫧', value: (aqi.o3 || 0).toFixed(1), label: 'O₃' });
    DOM.detailsGrid.innerHTML = cells.map(c => `<div class="mp-detail-cell"><div class="mp-detail-cell-icon">${c.icon}</div><div class="mp-detail-cell-value">${c.value}</div><div class="mp-detail-cell-label">${c.label}</div></div>`).join('');
}

function renderForecastList() {
    const days = state.forecast.forecast.forecastday, dayLabels = ['今天', '明天', '后天'];
    DOM.forecastContainer.innerHTML = days.map((day, i) => {
        const dayData = day.day, icon = getWeatherIcon(dayData.condition.code, true);
        return `<div class="mp-forecast-item"><div><div class="mp-forecast-day-label">${dayLabels[i]}</div><div class="mp-forecast-day-date">${day.date}</div></div><div class="mp-forecast-icon">${icon}</div><div class="mp-forecast-info"><div class="mp-forecast-condition">${dayData.condition.text}</div><div class="mp-forecast-extra">💧 ${dayData.avghumidity}% · 🌧️ ${dayData.totalprecip_mm}mm · UV ${dayData.uv}</div></div><div class="mp-forecast-temps"><span class="mp-forecast-high">${Math.round(dayData.maxtemp_c)}°</span><span class="mp-forecast-low">${Math.round(dayData.mintemp_c)}°</span></div></div>`;
    }).join('');
}

function renderAQI() {
    const aqi = state.currentWeather.current.air_quality || {}, pm25 = aqi.pm2_5;
    if (pm25 === undefined) { DOM.aqiContent.innerHTML = '<div style="text-align:center;color:var(--mp-text-muted);padding:12px;">暂无空气质量数据</div>'; return; }
    const level = pm25 < 35 ? '优' : pm25 < 75 ? '良' : '差', levelClass = pm25 < 35 ? 'good' : pm25 < 75 ? 'moderate' : 'unhealthy';
    DOM.aqiContent.innerHTML = `<div class="mp-aqi-score-circle ${levelClass}"><span class="mp-aqi-score-num">${pm25.toFixed(0)}</span></div>
    <div class="mp-aqi-label">PM2.5 · 空气质量 ${level}</div><div class="mp-aqi-details-row"><div class="mp-aqi-pollutant">
    <div class="mp-aqi-pollutant-value">${(aqi.pm10||0).toFixed(1)}</div><div class="mp-aqi-pollutant-name">PM10 µg/m³</div>
    </div><div class="mp-aqi-pollutant"><div class="mp-aqi-pollutant-value">${(aqi.o3||0).toFixed(1)}</div>
    <div class="mp-aqi-pollutant-name">O₃ µg/m³</div></div><div class="mp-aqi-pollutant"><div class="mp-aqi-pollutant-value">${(aqi.no2||0).
    toFixed(1)}</div><div class="mp-aqi-pollutant-name">NO₂ µg/m³</div></div><div class="mp-aqi-pollutant"><div class="mp-aqi-pollutant-value">
    ${(aqi.so2||0).toFixed(1)}</div><div class="mp-aqi-pollutant-name">SO₂ µg/m³</div></div></div>`;
}

/* 出行建议 */
function generateTravelAdvice() {
    const w = state.currentWeather.current, day = state.forecast.forecast.forecastday[0].day, 
    tomorrow = state.forecast.forecast.forecastday[1]?.day, code = w.condition.code;
    let score = 100; const warnings = [], suggestions = []; let clothing = [], activities = [], scoreLevel = 'excellent',
     scoreText = '非常适合出行！';
    if (w.temp_c < 0) { score -= 25; warnings.push('天气寒冷，注意保暖防冻'); } else if (w.temp_c < 10) { score -= 15; warnings.push('气温较低，注意保暖'); } else if (w.temp_c < 15) score -= 8; else if (w.temp_c > 35) { score -= 20; warnings.push('高温天气，注意防暑降温'); } else if (w.temp_c > 30) { score -= 10; warnings.push('天气较热，注意防暑'); } else if (w.temp_c > 28) score -= 5;
    if (code >= 1192 && code <= 1201) { score -= 25; warnings.push('大雨天气，出行不便'); } else if (code >= 1180 && code <= 1191) { score -= 15; warnings.push('有降雨，建议带伞'); } else if (code >= 1150 && code <= 1171) { score -= 10; warnings.push('有小雨/毛毛雨'); } else if (code >= 1273 && code <= 1282) { score -= 20; warnings.push('雷暴天气，注意安全'); } else if (code >= 1063 && code <= 1072) { score -= 8; warnings.push('局部有降水'); } else if (code >= 1204 && code <= 1237) { score -= 18; warnings.push('有降雪/雨夹雪'); } else if (code >= 1240 && code <= 1264) { score -= 12; warnings.push('有阵雨/阵雪'); }
    if (w.wind_kph > 50) { score -= 20; warnings.push('大风天气，注意安全'); } else if (w.wind_kph > 30) { score -= 10; warnings.push('风力较大'); } else if (w.wind_kph > 20) score -= 5;
    if (w.vis_km < 1) { score -= 20; warnings.push('能见度极低，谨慎出行'); } else if (w.vis_km < 3) { score -= 10; warnings.push('能见度较低'); } else if (w.vis_km < 5) score -= 5;
    if (day.uv >= 8) { score -= 5; warnings.push('紫外线很强，注意防晒'); } else if (day.uv >= 6) suggestions.push('紫外线较强，建议涂抹防晒霜');
    if (w.humidity > 90) { score -= 5; warnings.push('湿度很大，体感闷热'); } else if (w.humidity < 20) { score -= 3; suggestions.push('空气干燥，注意补水'); }
    if (w.temp_c < 0) clothing = ['🧥 厚羽绒服', '🧣 围巾', '🧤 手套', '👢 雪地靴', '🧶 毛线帽'];
    else if (w.temp_c < 10) clothing = ['🧥 羽绒服/棉衣', '🧣 围巾', '👖 厚长裤', '🧦 厚袜子', '👞 靴子'];
    else if (w.temp_c < 18) clothing = ['🧥 薄外套/夹克', '👔 长袖', '👖 长裤', '🧣 薄围巾'];
    else if (w.temp_c < 25) clothing = ['👕 短袖/薄长袖', '👖 长裤', '🧥 薄外套（早晚备用）'];
    else if (w.temp_c < 32) clothing = ['👕 短袖/T恤', '🩳 短裤', '👗 裙子', '🧴 防晒霜', '🕶️ 墨镜'];
    else clothing = ['👕 轻薄透气衣物', '🩳 短裤', '🧴 防晒霜', '🕶️ 墨镜', '🧢 遮阳帽'];
    if (code >= 1063 && code <= 1264) { clothing.push('☂️ 雨伞/雨衣', '👟 防水鞋'); }
    if (score >= 85) activities = ['🏞️ 非常适合户外郊游、徒步', '🚴 适合骑行、跑步等运动', '📸 适合户外摄影', '🧺 适合野餐露营'];
    else if (score >= 65) activities = ['🚶 可以进行轻度户外活动', '🏛️ 适合参观博物馆、商场', '☕ 适合室内聚会', '⚠️ 建议关注天气变化'];
    else if (score >= 40) activities = ['🏠 建议以室内活动为主', '🎬 看电影、逛商场不错', '📚 适合在图书馆/咖啡厅', '⚠️ 出行请注意安全'];
    else activities = ['🏠 建议尽量待在室内', '🎮 在家追剧、玩游戏', '🍲 适合在家烹饪美食', '⚠️ 非必要不外出'];
    if (w.temp_c >= 20 && w.temp_c <= 30 && code === 1000) activities.unshift('✨ 今天天气极好，尽情享受吧！');
    if (tomorrow && tomorrow.condition.code >= 1063 && tomorrow.condition.code <= 1264 && code === 1000) suggestions.push('明天可能有雨，今天抓紧时间户外活动哦');
    score = Math.max(0, Math.min(100, score));
    if (score >= 85) { scoreLevel = 'excellent'; scoreText = '非常适合出行！'; } else if (score >= 65) { scoreLevel = 'good'; scoreText = '比较适合出行'; } else if (score >= 40) { scoreLevel = 'fair'; scoreText = '出行需谨慎'; } else { scoreLevel = 'poor'; scoreText = '不建议出行'; }
    return { score, scoreLevel, scoreText, warnings, suggestions, clothing, activities };
}

function renderAllTravelSections() {
    const advice = generateTravelAdvice(), circ = 2 * Math.PI * 40, dashOffset = circ - (advice.score / 100) * circ;
    DOM.scoreCard.innerHTML = `<div class="mp-score-ring"><svg class="mp-score-ring-svg" viewBox="0 0 100 100"><circle class="mp-score-ring-bg" cx="50" cy="50" r="40"/><circle class="mp-score-ring-fg ${advice.scoreLevel}" cx="50" cy="50" r="40" stroke-dasharray="${circ}" stroke-dashoffset="${dashOffset}"/></svg><span class="mp-score-num">${advice.score}</span></div><div class="mp-score-text">${advice.scoreText}</div><div class="mp-score-sub-text">综合出行评分（满分100）</div>`;
    DOM.clothingContent.innerHTML = advice.clothing.map(c => `<span class="mp-clothing-item">${c}</span>`).join('');
    DOM.activityContent.innerHTML = advice.activities.map((a, i) => `<div class="mp-activity-item"><span class="mp-activity-num">${i+1}</span><span>${a}</span></div>`).join('');
    if (advice.warnings.length > 0) { DOM.warningSection.style.display = 'block'; DOM.warningContent.innerHTML = advice.warnings.map(w => `<div class="mp-warning-item">⚠️ ${w}</div>`).join(''); } else DOM.warningSection.style.display = 'none';
    if (advice.suggestions.length > 0) { DOM.tipsSection.style.display = 'block'; DOM.tipsContent.innerHTML = advice.suggestions.map(s => `<div class="mp-tip-item">💡 ${s}</div>`).join(''); } else DOM.tipsSection.style.display = 'none';
}

function updateFavoriteButton() {
    const card = DOM.currentWeatherCard, existingBtn = card.querySelector('.mp-fav-btn');
    if (existingBtn) existingBtn.remove();
    const fav = isFavorite(state.currentCity), btn = document.createElement('button');
    btn.className = 'mp-fav-btn'; btn.style.cssText = `display:block;margin:10px auto 0;background:none;border:1px solid var(--mp-border);border-radius:20px;padding:6px 16px;font-size:12px;cursor:pointer;color:${fav?'#fa9d3b':'var(--mp-text-secondary)'}`;
    btn.textContent = fav ? '⭐ 已收藏' : '☆ 收藏城市';
    btn.addEventListener('click', function (e) { e.stopPropagation(); const r = toggleFavorite(state.currentCity, state.currentCountry); if (r) { this.textContent = isFavorite(state.currentCity) ? '⭐ 已收藏' : '☆ 收藏城市'; this.style.color = isFavorite(state.currentCity) ? '#fa9d3b' : 'var(--mp-text-secondary)'; } });
    card.appendChild(btn);
}

/* 收藏/历史渲染 */
function renderFavoritesList() {
    if (state.favorites.length === 0) { DOM.favoritesList.innerHTML = '<div class="mp-empty-state"><div class="mp-empty-icon">📌</div><p>还没有收藏城市</p><p class="mp-empty-hint">搜索城市后可以收藏</p></div>'; return; }
    DOM.favoritesList.innerHTML = state.favorites.map(f => `<div class="mp-fav-item" data-city="${escapeHtml(f.city)}"><span class="mp-fav-flag">${getCountryFlag(f.country)}</span><span class="mp-fav-city-name">${escapeHtml(f.city)}</span><span class="mp-fav-country">${escapeHtml(f.country||'')}</span><span class="mp-fav-remove" data-city="${escapeHtml(f.city)}">移除</span></div>`).join('');
    DOM.favoritesList.querySelectorAll('.mp-fav-item').forEach(item => item.addEventListener('click', function (e) { if (e.target.classList.contains('mp-fav-remove')) return; switchTab('home'); DOM.cityInput.value = this.dataset.city; queryWeather(this.dataset.city); }));
    DOM.favoritesList.querySelectorAll('.mp-fav-remove').forEach(btn => btn.addEventListener('click', function (e) { e.stopPropagation(); const city = this.dataset.city; state.favorites = state.favorites.filter(f => f.city !== city); saveFavorites(); renderFavoritesList(); showToast('已移除收藏'); }));
}

function renderHistoryList() {
    if (state.history.length === 0) { DOM.historyList.innerHTML = '<div class="mp-empty-state"><div class="mp-empty-icon">📋</div><p>暂无查询记录</p></div>'; return; }
    DOM.historyList.innerHTML = state.history.map(h => `<div class="mp-history-item" data-city="${escapeHtml(h.city)}"><span class="mp-history-flag">${getCountryFlag(h.country)}</span><span class="mp-history-city-name">${escapeHtml(h.city)}</span><span class="mp-history-country">${escapeHtml(h.country||'')}</span><span class="mp-history-time">${getRelativeTime(h.time)}</span></div>`).join('');
    DOM.historyList.querySelectorAll('.mp-history-item').forEach(item => item.addEventListener('click', function () { switchTab('home'); DOM.cityInput.value = this.dataset.city; queryWeather(this.dataset.city); }));
}

/* AI 聊天 */
function addWeatherContextToChat() {
    const w = state.currentWeather.current, loc = state.currentWeather.location, flag = getCountryFlag(loc.country);
    addBotMessage(`${flag} 已更新 <b>${escapeHtml(loc.name)}</b> 天气数据：${w.condition.text}，温度 ${Math.round(w.temp_c)}°C（体感 ${Math.round(w.feelslike_c)}°C），湿度 ${w.humidity}%，风速 ${w.wind_kph} km/h。`);
}

function addUserMessage(text) { const div = document.createElement('div'); div.className = 'mp-chat-msg mp-chat-msg-user'; div.innerHTML = `<div class="mp-chat-msg-avatar">👤</div><div class="mp-chat-bubble">${escapeHtml(text)}</div>`; DOM.chatMessages.appendChild(div); scrollChatBottom(); state.chatHistory.push({ role: 'user', content: text }); }
function addBotMessage(text) { const div = document.createElement('div'); div.className = 'mp-chat-msg mp-chat-msg-bot'; div.innerHTML = `<div class="mp-chat-msg-avatar">🤖</div><div class="mp-chat-bubble">${text}</div>`; DOM.chatMessages.appendChild(div); scrollChatBottom(); state.chatHistory.push({ role: 'assistant', content: text }); }
function showTypingIndicator() { const div = document.createElement('div'); div.className = 'mp-chat-msg mp-chat-msg-bot typing-msg'; div.innerHTML = '<div class="mp-chat-msg-avatar">🤖</div><div class="mp-chat-bubble"><div class="mp-typing-dots"><span></span><span></span><span></span></div></div>'; DOM.chatMessages.appendChild(div); scrollChatBottom(); return div; }
function scrollChatBottom() { DOM.chatMessages.scrollTop = DOM.chatMessages.scrollHeight; }

function localAIResponse(question) {
    const q = question.toLowerCase().trim(), w = state.currentWeather?.current, day = state.forecast?.forecast?.forecastday?.[0]?.day;
    if (!w) return '请先查询一个城市的天气，我才能结合天气数据回答你的出行问题哦！在上方搜索框输入城市名称即可。';
    const city = state.currentCity, flag = getCountryFlag(state.currentCountry), temp = Math.round(w.temp_c), condition = w.condition.text, humidity = w.humidity, wind = w.wind_kph, code = w.condition.code, uv = day?.uv || 0;
    if (/户外|运动|跑步|骑行|爬山|锻炼|健身|郊游|徒步|hiking|jogging/i.test(q)) {
        if (code >= 1180 && code <= 1264) return `🌧️ <b>不太适合户外运动</b><br><br>${flag} ${city}正在下雨（${condition}），建议室内运动。`;
        if (code >= 1273 && code <= 1282) return `⛈️ <b>千万不要户外运动！</b><br><br>${flag} ${city}有雷暴天气，非常危险！`;
        if (wind > 30) return `💨 <b>风太大，不适合户外运动</b><br><br>${flag} ${city}风速 ${wind} km/h。`;
        if (temp > 35) return `🥵 <b>太热了！</b><br><br>${flag} ${city}当前 ${temp}°C，不建议剧烈运动。`;
        if (temp < 5) return `🥶 <b>天气较冷</b><br><br>${flag} ${city}当前 ${temp}°C，运动前要充分热身。`;
        if (code === 1000 && temp >= 15 && temp <= 28 && wind < 20) return `✨ <b>非常适合户外运动！</b><br><br>${flag} ${city}天气完美！温度 ${temp}°C，${condition}。`;
        return `🤔 <b>${flag} ${city}户外运动评估</b><br><br>${condition}，${temp}°C，风速 ${wind} km/h。总体可以运动，注意调整强度。`;
    }
    if (/穿|衣服|着装|搭配|裙子|短袖|外套|棉袄|羽绒|clothes|wear/i.test(q)) {
        if (temp < 0) return `🥶 <b>${flag} ${city}非常冷！${temp}°C</b><br><br>厚羽绒服+围巾+手套+帽子+雪地靴。`;
        if (temp < 10) return `😬 <b>${flag} ${city}比较冷，${temp}°C</b><br><br>羽绒服/棉衣+毛衣+长裤+保暖鞋。`;
        if (temp < 18) return `🍂 <b>${flag} ${city}微凉，${temp}°C</b><br><br>薄外套+长袖+牛仔裤，早晚加一件。`;
        if (temp < 25) return `😊 <b>${flag} ${city}温暖舒适，${temp}°C</b><br><br>短袖/薄长袖+长裤，早晚薄外套。`;
        if (temp < 32) return `☀️ <b>${flag} ${city}比较热，${temp}°C</b><br><br>短袖+短裤/裙子+防晒霜+墨镜。`;
        return `🥵 <b>${flag} ${city}非常热！${temp}°C</b><br><br>轻薄透气衣物+防晒全套+多喝水。`;
    }
    if (/出行|出去玩|旅游|出游|旅行|游玩|出门|周末|今天|明天|travel|trip/i.test(q)) {
        const ad = generateTravelAdvice(); let r = `🗺️ <b>${flag} ${city}出行评估</b><br><br>📊 评分：<b>${ad.score}/100</b> — ${ad.scoreText}<br>🌤️ ${condition}，${temp}°C<br><br>`; if (ad.warnings.length) r += `⚠️ ${ad.warnings.map(w=>'• '+w).join('<br>')}<br><br>`; r += `🎯 ${ad.activities.map((a,i)=>`${i+1}. ${a}`).join('<br>')}<br><br>👗 ${ad.clothing.slice(0,3).join('、')}<br><br>祝出行愉快！🎉`; return r;
    }
    if (/雨|伞|rain|淋|降水|暴雨/i.test(q)) { if (code >= 1180 && code <= 1264) return `☔ <b>正在下雨，一定要带伞！</b><br><br>${flag} ${city}：${condition}，${w.precip_mm} mm。`; if (code >= 1063 && code <= 1072) return `🌦️ <b>局部有降雨</b><br><br>${flag} ${city}建议随身带伞。`; return `☀️ <b>${flag} ${city}暂无降雨</b><br><br>${condition}，暂时不需要带伞。`; }
    if (/防晒|紫外线|晒|uv|墨镜|太阳/i.test(q)) { if (uv>=8) return `☀️ <b>紫外线非常强！UV ${uv}</b><br><br>必须全面防晒！`; if (uv>=5) return `☀️ <b>紫外线较强，UV ${uv}</b><br><br>SPF30+防晒霜+墨镜+帽子。`; return `☁️ <b>紫外线较弱，UV ${uv}</b><br><br>日常防晒即可。`; }
    if (/空气|雾霾|pm2|pm10|污染|aqi|质量/i.test(q)) { const aq = w.air_quality||{},p=aq.pm2_5; if (p!==undefined) { let aq2=p<35?'😊 良好':p<75?'🤔 一般':'😷 污染较重'; return `🌁 <b>${flag} ${city}空气质量</b><br><br>PM2.5: ${p.toFixed(1)}<br>PM10: ${(aq.pm10||0).toFixed(1)}<br><br>${aq2}`; } return `${flag} ${city}暂无空气质量数据。`; }
    if (/冷|热|温度|几度|凉|暖|高温|低温/i.test(q)) return `🌡️ <b>${flag} ${city}当前 ${temp}°C</b><br><br>体感 ${Math.round(w.feelslike_c)}°C<br>最高 ${day?.maxtemp_c||'--'}° / 最低 ${day?.mintemp_c||'--'}°<br>湿度 ${humidity}%<br><br>${temp>=30?'🥵 挺热的！':temp>=20?'😊 舒适~':temp>=10?'🍂 有点凉。':'🥶 比较冷！'}`;
    if (/风|wind/i.test(q)) return `💨 <b>${flag} ${city}风力</b><br><br>风速 ${wind} km/h<br>风向 ${w.wind_dir}<br>阵风 ${w.gust_kph} km/h<br><br>${wind<12?'基本不影响':wind<20?'微风舒服':wind<30?'有点大':'注意安全'}`;
    if (/天气|weather|怎么样|如何|预报|气候/i.test(q)) { const fd=state.forecast?.forecast?.forecastday||[]; let r=`🌤️ <b>${flag} ${city}天气概况</b><br><br>📍 ${condition}，${temp}°C（体感${Math.round(w.feelslike_c)}°C）<br>💧 ${humidity}% | 💨 ${wind} km/h<br><br>`; if(fd.length){r+='<b>未来三天：</b><br>';const lb=['今天','明天','后天'];fd.forEach((f,i)=>r+=`• ${lb[i]}：${f.day.condition.text}，${Math.round(f.day.maxtemp_c)}°/${Math.round(f.day.mintemp_c)}°<br>`);} return r; }
    return `🤔 <b>关于"${escapeHtml(question)}"</b><br><br>${flag} ${city}当前${condition}，${temp}°C。<br><br>💡 可以问我：<br>• "适合户外运动吗？"<br>• "应该穿什么衣服？"<br>• "需要带伞吗？"<br>• "空气质量怎么样？"`;
}

async function cloudAIResponse(question) {
    const w = state.currentWeather?.current, day = state.forecast?.forecast?.forecastday?.[0]?.day, fdays = state.forecast?.forecast?.forecastday || [];
    let ctx = ''; if (w && state.currentCity) ctx = `你是专业天气出行顾问。基于以下数据回答用户问题：\n📍 ${state.currentCity}, ${state.currentCountry}\n🌤️ ${w.condition.text}\n🌡️ ${Math.round(w.temp_c)}°C（体感${Math.round(w.feelslike_c)}°C）\n💧 ${w.humidity}%\n💨 ${w.wind_kph} km/h ${w.wind_dir}\n📅 预报：${fdays.map(fd=>fd.date+' '+fd.day.condition.text+' '+Math.round(fd.day.maxtemp_c)+'°/'+Math.round(fd.day.mintemp_c)+'°').join('；')}\n用中文友好回答，300字以内。`;
    try { const resp = await fetch(CONFIG.AI_API_URL, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ model: CONFIG.AI_MODEL, messages: [{ role: 'system', content: ctx || '你是专业天气出行顾问，用中文回答。' }, { role: 'user', content: question }], max_tokens: 600, temperature: 0.7 }) }); if (!resp.ok) throw new Error('API fail'); const data = await resp.json(); return data.choices?.[0]?.message?.content || null; } catch (err) { console.warn('云端AI失败:', err.message); return null; }
}

async function handleChatMessage(text) {
    if (!text.trim()) return;
    DOM.chatInput.disabled = true; DOM.sendBtn.disabled = true; addUserMessage(text); DOM.chatInput.value = '';
    const typingEl = showTypingIndicator();
    let reply = null; if (state.currentWeather) reply = await cloudAIResponse(text);
    if (!reply) { await new Promise(r => setTimeout(r, 700 + Math.random() * 1000)); reply = localAIResponse(text); }
    typingEl.remove(); addBotMessage(reply); DOM.chatInput.disabled = false; DOM.sendBtn.disabled = false; DOM.chatInput.focus();
}

/* 搜索框事件 */
DOM.cityInput.addEventListener('focus', function () { const val = this.value.trim(); if (!val) openSearchPanel(); });
DOM.searchBtn.addEventListener('click', function () { const city = DOM.cityInput.value.trim(); if (!city) { showToast('请输入城市名称', '🔍', 1500); return; } closeSearchPanel(); DOM.searchClear.style.display = 'none'; queryWeather(city); });
DOM.cityInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') { const city = this.value.trim(); if (!city) return; closeSearchPanel(); DOM.searchClear.style.display = 'none'; queryWeather(city); } });
DOM.cityInput.addEventListener('input', function () { const val = this.value.trim(); DOM.searchClear.style.display = val ? 'flex' : 'none'; if (!DOM.searchPanel.classList.contains('active')) openSearchPanel(); clearTimeout(debounceTimer); debounceTimer = setTimeout(() => searchCities(val), CONFIG.DEBOUNCE_MS); });
DOM.searchClear.addEventListener('click', function () { DOM.cityInput.value = ''; DOM.searchClear.style.display = 'none'; DOM.panelSuggestions.style.display = 'none'; DOM.panelSuggestions.innerHTML = ''; DOM.panelDomestic.style.display = ''; DOM.panelInternational.style.display = 'none'; document.querySelectorAll('.mp-panel-tab').forEach(t => t.classList.remove('active')); const dt = document.querySelector('.mp-panel-tab[data-tab="domestic"]'); if (dt) dt.classList.add('active'); DOM.cityInput.focus(); });
document.addEventListener('click', function (e) { if (!DOM.searchPanel.contains(e.target) && e.target !== DOM.cityInput) DOM.searchPanel.classList.remove('active'); });
DOM.searchPanel.addEventListener('click', function (e) { e.stopPropagation(); });

/* 城市标签 */
document.querySelectorAll('.mp-city-chip').forEach(chip => chip.addEventListener('click', function () { DOM.cityInput.value = this.dataset.city; DOM.searchClear.style.display = 'flex'; closeSearchPanel(); queryWeather(this.dataset.city); }));

/* 聊天 */
DOM.sendBtn.addEventListener('click', function () { handleChatMessage(DOM.chatInput.value.trim()); });
DOM.chatInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); handleChatMessage(this.value.trim()); } });
DOM.chatMessages.addEventListener('click', function (e) { const qb = e.target.closest('.mp-quick-q'); if (qb) handleChatMessage(qb.dataset.question); });

/* 个人中心 */
DOM.editFavorites.addEventListener('click', function () { showToast('点击城市可查询，点击"移除"可删除', '📝', 2000); });
DOM.clearHistory.addEventListener('click', function () { state.history = []; saveHistory(); renderHistoryList(); showToast('已清空查询记录', '🗑️', 1500); });

/* 导航 */
DOM.navShare.addEventListener('click', function () { const w = state.currentWeather?.current, text = w ? `🌤️ ${state.currentCity}：${w.condition.text}，${Math.round(w.temp_c)}°C` : '天气出行助手'; if (navigator.share) navigator.share({ title: '天气出行助手', text }).catch(()=>{}); else navigator.clipboard.writeText(text).then(()=>showToast('已复制', '📋', 1500)).catch(()=>showToast(text, '📤', 2000)); });
DOM.navMore.addEventListener('click', function () { showToast('天气出行助手 v2.0 · AI驱动', 'ℹ️', 1800); });

/* 初始化 */
function init() {
    loadFavorites(); loadHistory(); renderFavoritesList(); renderHistoryList();
    const now = new Date(); DOM.chatDateLabel.textContent = `${now.getFullYear()}年${now.getMonth()+1}月${now.getDate()}日`;
    setTimeout(() => queryWeather(CONFIG.DEFAULT_CITY), 300);
}
document.addEventListener('DOMContentLoaded', init);
