// Language selector functionality
const languageOptions = [
  { name: 'Auto Detect', code: 'auto', recommended: true },
  { name: 'English', code: 'eng' },
  { name: 'Sinhala', code: 'sin' },
  { name: 'Tamil', code: 'tam' },
  { name: 'Chinese (Simplified)', code: 'chi_sim' },
  { name: 'Middle English', code: 'enm' },
  { name: 'Math/Equation', code: 'equ' },
  { name: 'French', code: 'fra' },
  { name: 'Middle French', code: 'frm' },
  { name: 'Hindi', code: 'hin' },
  { name: 'Italian', code: 'ita' },
  { name: 'Italian (Old)', code: 'ita_old' },
  { name: 'Japanese', code: 'jpn' },
  { name: 'Japanese (Vertical)', code: 'jpn_vert' },
  { name: 'Korean', code: 'kor' },
  { name: 'Orientation/Script Detection', code: 'osd' },
  { name: 'Spanish', code: 'spa' },
  { name: 'Arabic', code: 'ara' }
];

let selectedLanguages = [];

// Initialize language selector
function initLanguageSelector() {
  const selector = document.getElementById('languageSelector');
  const dropdown = document.getElementById('languageDropdown');
  const search = document.getElementById('languageSearch');
  
  // Toggle dropdown
  selector.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleLanguageDropdown();
  });
  
  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!selector.contains(e.target) && !dropdown.contains(e.target)) {
      closeLanguageDropdown();
    }
  });
  
  // Search functionality
  search.addEventListener('input', filterLanguages);
  search.addEventListener('click', (e) => e.stopPropagation());
  
  // Populate initial options
  renderLanguageOptions();
}

function toggleLanguageDropdown() {
  const selector = document.getElementById('languageSelector');
  const dropdown = document.getElementById('languageDropdown');
  
  if (dropdown.classList.contains('open')) {
    closeLanguageDropdown();
  } else {
    selector.classList.add('open');
    dropdown.classList.add('open');
    document.getElementById('languageSearch').focus();
  }
}

function closeLanguageDropdown() {
  const selector = document.getElementById('languageSelector');
  const dropdown = document.getElementById('languageDropdown');
  const search = document.getElementById('languageSearch');
  
  selector.classList.remove('open');
  dropdown.classList.remove('open');
  search.value = '';
  renderLanguageOptions();
}

function filterLanguages() {
  const searchTerm = document.getElementById('languageSearch').value.toLowerCase();
  renderLanguageOptions(searchTerm);
}

function renderLanguageOptions(searchTerm = '') {
  const optionsContainer = document.getElementById('languageOptions');
  const availableLanguages = languageOptions.filter(lang => 
    !selectedLanguages.some(selected => selected.code === lang.code) &&
    lang.name.toLowerCase().includes(searchTerm)
  );
  
  if (availableLanguages.length === 0) {
    optionsContainer.innerHTML = '<div class="no-results">No languages found</div>';
    return;
  }
  
  optionsContainer.innerHTML = availableLanguages.map(lang => `
    <div class="language-option ${lang.recommended ? 'recommended' : ''}" 
         onclick="selectLanguage('${lang.code}')">
      ${lang.name} ${lang.recommended ? '(Recommended)' : ''}
    </div>
  `).join('');
}

function selectLanguage(code) {
  const language = languageOptions.find(lang => lang.code === code);
  
  if (language.code === 'auto') {
    selectedLanguages = [language];
  } else {
    selectedLanguages = selectedLanguages.filter(lang => lang.code !== 'auto');
    selectedLanguages.push(language);
  }
  
  updateSelectedLanguagesDisplay();
  closeLanguageDropdown();
}

function removeLanguage(code) {
  selectedLanguages = selectedLanguages.filter(lang => lang.code !== code);
  updateSelectedLanguagesDisplay();
}

function updateSelectedLanguagesDisplay() {
  const container = document.getElementById('selectedLanguages');
  
  if (selectedLanguages.length === 0) {
    container.innerHTML = '<span class="placeholder">Select languages...</span>';
    return;
  }
  
  container.innerHTML = selectedLanguages.map(lang => `
    <span class="language-tag">
      ${lang.name}
      <i class="fa-solid fa-xmark remove-btn" onclick="removeLanguage('${lang.code}')"></i>
    </span>
  `).join('');
}

function getSelectedLanguagesForBackend() {
  if (selectedLanguages.length === 0) return '';
  if (selectedLanguages.some(lang => lang.code === 'auto')) return 'auto';
  return selectedLanguages.map(lang => lang.code).join('+');
}

document.addEventListener('DOMContentLoaded', initLanguageSelector);