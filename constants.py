region_mapping = {
    # North America
    'United States': 'North America', 'Canada': 'North America', 'Mexico': 'North America',
    'Greenland': 'North America', 'Bermuda': 'North America',
    
    # Central America & Caribbean
    'Guatemala': 'Latin America', 'Honduras': 'Latin America', 'El Salvador': 'Latin America',
    'Nicaragua': 'Latin America', 'Costa Rica': 'Latin America', 'Panama': 'Latin America',
    'Belize': 'Latin America', 'Jamaica': 'Latin America', 'Haiti': 'Latin America',
    'Dominican Republic': 'Latin America', 'Cuba': 'Latin America', 'Bahamas, The': 'Latin America',
    'Trinidad and Tobago': 'Latin America', 'Barbados': 'Latin America', 'St. Lucia': 'Latin America',
    'Grenada': 'Latin America', 'St. Vincent and the Grenadines': 'Latin America',
    'Antigua and Barbuda': 'Latin America', 'Dominica': 'Latin America', 'St. Kitts and Nevis': 'Latin America',
    'Aruba': 'Latin America', 'Curacao': 'Latin America', 'Sint Maarten (Dutch part)': 'Latin America',
    'St. Martin (French part)': 'Latin America', 'Turks and Caicos Islands': 'Latin America',
    'Cayman Islands': 'Latin America', 'British Virgin Islands': 'Latin America', 
    'Virgin Islands (U.S.)': 'Latin America', 'Puerto Rico': 'Latin America',
    
    # South America
    'Brazil': 'Latin America', 'Argentina': 'Latin America', 'Chile': 'Latin America',
    'Colombia': 'Latin America', 'Peru': 'Latin America', 'Venezuela, RB': 'Latin America',
    'Ecuador': 'Latin America', 'Bolivia': 'Latin America', 'Paraguay': 'Latin America',
    'Uruguay': 'Latin America', 'Guyana': 'Latin America', 'Suriname': 'Latin America',
    
    # Europe
    'Germany': 'Europe', 'United Kingdom': 'Europe', 'France': 'Europe', 'Italy': 'Europe',
    'Spain': 'Europe', 'Poland': 'Europe', 'Romania': 'Europe', 'Netherlands': 'Europe',
    'Belgium': 'Europe', 'Czechia': 'Europe', 'Greece': 'Europe', 'Portugal': 'Europe',
    'Sweden': 'Europe', 'Hungary': 'Europe', 'Austria': 'Europe', 'Bulgaria': 'Europe',
    'Denmark': 'Europe', 'Finland': 'Europe', 'Slovakia': 'Europe', 'Norway': 'Europe',
    'Ireland': 'Europe', 'Croatia': 'Europe', 'Bosnia and Herzegovina': 'Europe',
    'Albania': 'Europe', 'Lithuania': 'Europe', 'Slovenia': 'Europe', 'Latvia': 'Europe',
    'North Macedonia': 'Europe', 'Estonia': 'Europe', 'Moldova': 'Europe', 'Malta': 'Europe',
    'Luxembourg': 'Europe', 'Montenegro': 'Europe', 'Cyprus': 'Europe', 'Iceland': 'Europe',
    'Andorra': 'Europe', 'Liechtenstein': 'Europe', 'Monaco': 'Europe', 'San Marino': 'Europe',
    'Serbia': 'Europe', 'Switzerland': 'Europe', 'Ukraine': 'Europe', 'Belarus': 'Europe',
    'Kosovo': 'Europe', 'Channel Islands': 'Europe', 'Faroe Islands': 'Europe', 'Gibraltar': 'Europe',
    'Isle of Man': 'Europe', 'Russian Federation': 'Europe', 'Turkiye': 'Europe',
    
    # Asia-Pacific
    'China': 'Asia-Pacific', 'Japan': 'Asia-Pacific', 'India': 'Asia-Pacific', 
    'Korea, Rep.': 'Asia-Pacific', 'Indonesia': 'Asia-Pacific', 'Thailand': 'Asia-Pacific',
    'Singapore': 'Asia-Pacific', 'Malaysia': 'Asia-Pacific', 'Philippines': 'Asia-Pacific',
    'Vietnam': 'Asia-Pacific', 'Bangladesh': 'Asia-Pacific', 'Pakistan': 'Asia-Pacific',
    'Myanmar': 'Asia-Pacific', 'Sri Lanka': 'Asia-Pacific', 'Nepal': 'Asia-Pacific',
    'Cambodia': 'Asia-Pacific', 'Lao PDR': 'Asia-Pacific', 'Mongolia': 'Asia-Pacific',
    'Brunei Darussalam': 'Asia-Pacific', 'Timor-Leste': 'Asia-Pacific', 'Bhutan': 'Asia-Pacific',
    'Maldives': 'Asia-Pacific', 'Hong Kong SAR, China': 'Asia-Pacific', 'Macao SAR, China': 'Asia-Pacific',
    'Australia': 'Asia-Pacific', 'New Zealand': 'Asia-Pacific', 'Papua New Guinea': 'Asia-Pacific',
    'Fiji': 'Asia-Pacific', 'Solomon Islands': 'Asia-Pacific', 'Vanuatu': 'Asia-Pacific',
    'Samoa': 'Asia-Pacific', 'Kiribati': 'Asia-Pacific', 'Tonga': 'Asia-Pacific',
    'Micronesia, Fed. Sts.': 'Asia-Pacific', 'Palau': 'Asia-Pacific', 'Marshall Islands': 'Asia-Pacific',
    'Nauru': 'Asia-Pacific', 'Tuvalu': 'Asia-Pacific', 'American Samoa': 'Asia-Pacific',
    'Guam': 'Asia-Pacific', 'Northern Mariana Islands': 'Asia-Pacific', 'French Polynesia': 'Asia-Pacific',
    'New Caledonia': 'Asia-Pacific', 'Korea, Dem. People\'s Rep.': 'Asia-Pacific',
    
    # Middle East
    'Saudi Arabia': 'Middle East', 'United Arab Emirates': 'Middle East', 'Turkey': 'Middle East',
    'Iran, Islamic Rep.': 'Middle East', 'Iraq': 'Middle East', 'Israel': 'Middle East',
    'Qatar': 'Middle East', 'Kuwait': 'Middle East', 'Oman': 'Middle East', 'Lebanon': 'Middle East',
    'Jordan': 'Middle East', 'Bahrain': 'Middle East', 'Yemen, Rep.': 'Middle East',
    'West Bank and Gaza': 'Middle East', 'Syrian Arab Republic': 'Middle East',
    
    # Central Asia
    'Kazakhstan': 'Central Asia', 'Uzbekistan': 'Central Asia', 'Turkmenistan': 'Central Asia',
    'Kyrgyz Republic': 'Central Asia', 'Tajikistan': 'Central Asia', 'Afghanistan': 'Central Asia',
    'Armenia': 'Central Asia', 'Georgia': 'Central Asia', 'Azerbaijan': 'Central Asia',
    
    # Africa
    'Nigeria': 'Africa', 'South Africa': 'Africa', 'Egypt, Arab Rep.': 'Africa',
    'Algeria': 'Africa', 'Morocco': 'Africa', 'Kenya': 'Africa', 'Ethiopia': 'Africa',
    'Ghana': 'Africa', 'Tanzania': 'Africa', 'Angola': 'Africa', "Cote d'Ivoire": 'Africa',
    'Uganda': 'Africa', 'Cameroon': 'Africa', 'Libya': 'Africa', 'Tunisia': 'Africa',
    'Senegal': 'Africa', 'Zimbabwe': 'Africa', 'Sudan': 'Africa', 'Mali': 'Africa',
    'Burkina Faso': 'Africa', 'Mozambique': 'Africa', 'Zambia': 'Africa', 'Madagascar': 'Africa',
    'Botswana': 'Africa', 'Namibia': 'Africa', 'Mauritius': 'Africa', 'Gabon': 'Africa',
    'Guinea': 'Africa', 'Chad': 'Africa', 'Rwanda': 'Africa', 'Benin': 'Africa',
    'Burundi': 'Africa', 'South Sudan': 'Africa', 'Togo': 'Africa', 'Sierra Leone': 'Africa',
    'Malawi': 'Africa', 'Eritrea': 'Africa', 'Mauritania': 'Africa', 'Liberia': 'Africa',
    'Central African Republic': 'Africa', 'Lesotho': 'Africa', 'Cabo Verde': 'Africa',
    'Eswatini': 'Africa', 'Djibouti': 'Africa', 'Comoros': 'Africa', 'Equatorial Guinea': 'Africa',
    'Guinea-Bissau': 'Africa', 'Gambia, The': 'Africa', 'Seychelles': 'Africa',
    'Sao Tome and Principe': 'Africa', 'Somalia': 'Africa', 'Congo, Rep.': 'Africa',
    'Congo, Dem. Rep.': 'Africa', 'Niger': 'Africa',
}