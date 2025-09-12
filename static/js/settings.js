const updateBtn = document.querySelector("#update");
const userId = document.querySelector("#userid").innerHTML;
const deleteAccount = document.querySelector("#delete-account");

// * Get saved settings from server
async function getSavedSettings() {
    const rawsettings = await fetch(`/api/user-settings/?user-id=${userId}`)
    const settings = await rawsettings.json();

    console.log(settings);
    return settings;
}

// | Add this CSS for active states
const style = document.createElement('style');
style.textContent = `
    .btn.active, .icon-btn.active {
        border: 5px solid var(--background) !important;
        outline: 2px solid var(--border) !important;
    }
    .switch-box.active {
        background-color: var(--accent-1) !important;
    }
    .switch-box.active .switch-ball {
        transform: translateX(40px);
    }
`;
document.head.appendChild(style);

// * Initialize version state
function initializeVersionState() {
    const stableBtn = document.getElementById('stable-v');
    const preReleaseBtn = document.getElementById('pre-release');
    
    stableBtn.addEventListener('click', function() {
        stableBtn.classList.add('active');
        preReleaseBtn.classList.remove('active');
        preReleaseBtn.textContent = 'Switch to pre-release version';
    });
    
    preReleaseBtn.addEventListener('click', function() {
        preReleaseBtn.classList.add('active');
        stableBtn.classList.remove('active');
        preReleaseBtn.textContent = 'Using pre-release';
    });
}

// * Initialize active states from current selections
async function initializeSettings() {
    try {
        const savedSettings = await getSavedSettings();
        
        // Initialize appearance settings
        initializeAppearanceSettings(savedSettings.appearance);
        
        // Initialize profile settings
        initializeProfileSettings(savedSettings.profile);
        
        // Initialize security settings
        initializeSecuritySettings(savedSettings.security);
        
        // Initialize advanced settings
        initializeAdvancedSettings(savedSettings.advanced);
        
        // Initialize version state (should come after advanced settings)
        initializeVersionState(savedSettings.advanced);
        
    } catch (error) {
        console.error('Failed to load saved settings:', error);
        setDefaultSettings();
    }
}

// Helper functions for each settings section
function initializeAppearanceSettings(appearance) {
    if (!appearance) return;
    
    // Set theme
    if (appearance.theme) {
        document.querySelectorAll('#theme .btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(appearance.theme)?.classList.add('active');
    }
    
    // Set accent color
    if (appearance.accent) {
        document.querySelectorAll('#accent .btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(appearance.accent)?.classList.add('active');
    }
    
    // Set chart color scheme
    if (appearance.chartColor) {
        document.querySelectorAll('#chart-color .btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(appearance.chartColor)?.classList.add('active');
    }
    
    // Set chart type
    if (appearance.chartType) {
        document.querySelectorAll('#chart-type .icon-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(appearance.chartType)?.classList.add('active');
    }
}

function initializeProfileSettings(profile) {
    if (!profile) return;
    
    // Set skills
    if (profile.skills && Array.isArray(profile.skills)) {
        const skillInputs = document.querySelectorAll('#skills input');
        profile.skills.forEach((skill, index) => {
            if (skillInputs[index]) {
                skillInputs[index].value = skill;
            }
        });
    }
    
    // Set working hours
    if (profile.workingHours) {
        if (profile.workingHours.from) {
            document.getElementById('from_').value = profile.workingHours.from;
        }
        if (profile.workingHours.to) {
            document.getElementById('to_').value = profile.workingHours.to;
        }
    }
    
    if (profile.socialLinks && Array.isArray(profile.socialLinks)) {
        const titleInputs = document.querySelectorAll("#social-links .input.title")
        const urlInputs = document.querySelectorAll("#social-links .input.addr")

        profile.socialLinks.forEach((data, index) => {
            if (titleInputs[index]) {titleInputs[index].value = data.title}
            if (urlInputs[index]) {urlInputs[index].value = data.url}
        });
    }
}

function initializeSecuritySettings(security) {
    if (!security) return;
    
    // Set password rotation toggle
    if (security.passwordRotation !== undefined) {
        const switchBox = document.querySelector('#pwd-rotation .switch-box');
        if (security.passwordRotation) {
            switchBox.classList.add('active');
        } else {
            switchBox.classList.remove('active');
        }
    }
}

function initializeAdvancedSettings(advanced) {
    if (!advanced) return;
    
    // This will be used by initializeVersionState
    // You can add more advanced settings here later
}

function initializeVersionState(advanced) {
    const stableBtn = document.getElementById('stable-v');
    const preReleaseBtn = document.getElementById('pre-release');
    
    // Set initial state based on saved settings
    if (advanced && advanced.preRelease) {
        preReleaseBtn.classList.add('active');
        stableBtn.classList.remove('active');
        preReleaseBtn.textContent = 'Using pre-release';
    } else {
        stableBtn.classList.add('active');
        preReleaseBtn.classList.remove('active');
        preReleaseBtn.textContent = 'Switch to pre-release version';
    }
    
    // & Add click handlers
    stableBtn.addEventListener('click', function() {
        stableBtn.classList.add('active');
        preReleaseBtn.classList.remove('active');
        preReleaseBtn.textContent = 'Switch to pre-release version';
    });
    
    preReleaseBtn.addEventListener('click', function() {
        preReleaseBtn.classList.add('active');
        stableBtn.classList.remove('active');
        preReleaseBtn.textContent = 'Using pre-release';
    });
}

// * Fallback to default settings
function setDefaultSettings() {
    document.getElementById('light').classList.add('active');
    document.getElementById('blue').classList.add('active');
    document.getElementById('classic').classList.add('active');
    document.getElementById('doughnut').classList.add('active');
    
    // Initialize version state with defaults
    const stableBtn = document.getElementById('stable-v');
    const preReleaseBtn = document.getElementById('pre-release');
    stableBtn.classList.add('active');
    preReleaseBtn.textContent = 'Switch to pre-release version';
}

// * Update getSavedSettings to handle errors
async function getSavedSettings() {
    try {
        const rawsettings = await fetch(`/api/user-settings/?user-id=${userId}`);
        if (!rawsettings.ok) {
            throw new Error(`HTTP error! status: ${rawsettings.status}`);
        }
        const settings = await rawsettings.json();
        return settings;
    } catch (error) {
        console.error('Error fetching settings:', error);
        throw error;
    }
}

// & Add click handlers to toggle active states
document.querySelectorAll('#theme .btn, #accent .btn, #chart-color .btn').forEach(btn => {
    btn.addEventListener('click', function() {
        // ! Remove active class from siblings
        this.parentElement.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
        // ! Add active class to clicked button
        this.classList.add('active');
    });
});

document.querySelectorAll('#chart-type .icon-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        this.parentElement.querySelectorAll('.icon-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
    });
});

// & Toggle switch functionality
document.querySelector('#pwd-rotation .switch-box').addEventListener('click', function() {
    this.classList.toggle('active');
});

function collectAllSettings() {
    // Helper function to get active button value
    function getActiveValue(containerId) {
        const activeBtn = document.querySelector(`#${containerId} .btn.active`);
        return activeBtn ? activeBtn.id : null;
    }

    // Helper function to get active icon button value
    function getActiveIconValue(containerId) {
        const activeBtn = document.querySelector(`#${containerId} .icon-btn.active`);
        return activeBtn ? activeBtn.id : null;
    }

    // Helper function to get input values
    function getInputValues(containerId) {
        return Array.from(document.querySelectorAll(`#${containerId} input`))
            .map(input => input.value.trim())
            .filter(value => value !== '');
    }

    // Get version information
    function getVersionInfo() {
        const isPreRelease = document.getElementById('pre-release').classList.contains('active');
        return {
            currentVersion: isPreRelease ? 'pre-release' : 'v0.9.0',
            isPreRelease: isPreRelease,
            versionNumber: isPreRelease ? 'v1.0.0-beta' : 'v0.9.0'
        };
    }

    return {
        appearance: {
            theme: getActiveValue('theme'),
            accent: getActiveValue('accent'),
            chartColor: getActiveValue('chart-color'),
            chartType: getActiveIconValue('chart-type')
        },
        profile: {
            skills: getInputValues('skills'),
            workingHours: {
                from: document.getElementById('from_').value,
                to: document.getElementById('to_').value
            },
            socialLinks: Array.from(document.querySelectorAll('#social-links .row'))
                .map(row => {
                    const title = row.querySelector('.title').value.trim();
                    const url = row.querySelector('.addr').value.trim();
                    return title && url ? { title, url } : null;
                })
                .filter(link => link !== null)
        },
        security: {
            passwordRotation: document.querySelector('#pwd-rotation .switch-box').classList.contains('active')
        },
        advanced: {
            version: getVersionInfo(),
        },
    };
}

// & socket listener for update-settings-callback
socket.on('update-settings-callback', (data) => {
    if (data.status == 200) {
        window.location.reload();
    } else if (data.status == 404) {
        window.open('/auth/signup', "_self");
        alert("Your account is not properly updated.");
    } else {
        alert("Something went wrong.")
    }
})

updateBtn.addEventListener('click', () => {
    settings = collectAllSettings();
    console.log(settings);    
    socket.emit('update-settings', settings);
})
initializeSettings();

// & Event listener for delete-account btn
deleteAccount.addEventListener('click', () => {
    let confirmation = confirm("Are you sure to delete this account permanently?")
    if (confirmation) {
        window.open("/auth/delete", "_blank");
    }
})