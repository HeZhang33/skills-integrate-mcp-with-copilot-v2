// Enhanced Event Management System with Points & Leaderboard
let currentUser = {
    email: '',
    name: '',
    points: 0,
    rank: 0
};

let allEvents = [];
let leaderboardData = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadEvents();
    loadLeaderboard();
    loadBadges();
    
    // Show events tab by default
    showTab('events');
});

// Tab Management
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Load tab-specific content
    if (tabName === 'leaderboard') {
        loadLeaderboard();
    } else if (tabName === 'badges') {
        loadBadges();
    } else if (tabName === 'profile' && currentUser.email) {
        loadUserProfile();
    }
}

// User Management
function setUserInfo() {
    const email = document.getElementById('student-email').value;
    const name = document.getElementById('student-name').value;
    
    if (!email || !name) {
        showMessage('Please enter both email and name', 'error');
        return;
    }
    
    if (!email.includes('@mergington.edu')) {
        showMessage('Please use a valid Mergington High School email', 'error');
        return;
    }
    
    currentUser.email = email;
    currentUser.name = name;
    
    // Show user points display
    document.getElementById('user-points-display').classList.remove('hidden');
    updateUserPointsDisplay();
    
    showMessage(`Welcome, ${name}! You can now register for events.`, 'success');
}

function updateUserPointsDisplay() {
    // Get user ranking from leaderboard
    fetch('/leaderboard/user/' + encodeURIComponent(currentUser.email))
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            return { ranking: { total_points: 0, rank: '--', badges_count: 0 } };
        })
        .then(data => {
            currentUser.points = data.ranking.total_points;
            currentUser.rank = data.ranking.rank;
            
            document.getElementById('current-points').textContent = data.ranking.total_points;
            document.getElementById('current-rank').textContent = '#' + data.ranking.rank;
            document.getElementById('badge-count').textContent = data.ranking.badges_count;
        })
        .catch(error => {
            console.log('User not found in leaderboard yet');
            document.getElementById('current-points').textContent = '0';
            document.getElementById('current-rank').textContent = '#--';
            document.getElementById('badge-count').textContent = '0';
        });
}

// Events Management
function loadEvents() {
    fetch('/events')
        .then(response => response.json())
        .then(data => {
            allEvents = data.events || [];
            displayEvents(allEvents);
        })
        .catch(error => {
            console.error('Error loading events:', error);
            document.getElementById('events-list').innerHTML = '<p>Error loading events. Please try again later.</p>';
        });
}

function displayEvents(events) {
    const eventsContainer = document.getElementById('events-list');
    
    if (events.length === 0) {
        eventsContainer.innerHTML = '<p>No events available at the moment.</p>';
        return;
    }
    
    const eventsHTML = events.map(event => {
        const isRegistered = event.participants.some(p => p.email === currentUser.email);
        const isFull = event.participants.length >= event.max_participants;
        
        return `
            <div class="event-card">
                <div class="event-header">
                    <h4 class="event-title">${event.name}</h4>
                    <span class="event-type ${event.event_type}">${event.event_type.toUpperCase()}</span>
                </div>
                
                <div class="event-details">
                    <div class="event-detail">
                        <i class="fas fa-info-circle"></i>
                        ${event.description}
                    </div>
                    <div class="event-detail">
                        <i class="fas fa-user-tie"></i>
                        Organizer: ${event.organizer}
                    </div>
                    <div class="event-detail">
                        <i class="fas fa-clock"></i>
                        ${event.schedule}
                    </div>
                    <div class="event-detail">
                        <i class="fas fa-calendar"></i>
                        Event Date: ${new Date(event.event_date).toLocaleDateString()}
                    </div>
                    <div class="event-detail">
                        <i class="fas fa-users"></i>
                        Participants: ${event.participants.length}/${event.max_participants}
                    </div>
                    ${event.event_type === 'paid' ? `
                        <div class="event-detail">
                            <i class="fas fa-dollar-sign"></i>
                            Fee: $${event.fee}
                        </div>
                    ` : ''}
                    ${event.whatsapp_group ? `
                        <div class="event-detail">
                            <i class="fab fa-whatsapp"></i>
                            WhatsApp Group Available
                        </div>
                    ` : ''}
                </div>
                
                <div class="event-actions">
                    ${!currentUser.email ? `
                        <button class="btn-primary" disabled>Set User Info First</button>
                    ` : isRegistered ? `
                        <button class="btn-danger" onclick="unregisterFromEvent('${event.id}')">
                            Unregister
                        </button>
                        <button class="btn-success" onclick="markAttendance('${event.id}')">
                            Mark Attendance
                        </button>
                        <button class="btn-success" onclick="completeEvent('${event.id}')">
                            Complete Event
                        </button>
                    ` : isFull ? `
                        <button class="btn-primary" disabled>Event Full</button>
                    ` : `
                        <button class="btn-primary" onclick="registerForEvent('${event.id}')">
                            Register (+5 points)
                        </button>
                    `}
                </div>
            </div>
        `;
    }).join('');
    
    eventsContainer.innerHTML = eventsHTML;
}

function registerForEvent(eventId) {
    if (!currentUser.email || !currentUser.name) {
        showMessage('Please set your user information first', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('user_email', currentUser.email);
    formData.append('user_name', currentUser.name);
    
    fetch(`/events/${eventId}/register`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showMessage(`${data.message} (+${data.points_earned} points!)`, 'success');
            loadEvents(); // Reload events to update registration status
            updateUserPointsDisplay(); // Update points display
        } else if (data.detail) {
            showMessage(data.detail, 'error');
        }
    })
    .catch(error => {
        console.error('Registration error:', error);
        showMessage('Registration failed. Please try again.', 'error');
    });
}

function unregisterFromEvent(eventId) {
    const formData = new FormData();
    formData.append('user_email', currentUser.email);
    
    fetch(`/events/${eventId}/unregister`, {
        method: 'DELETE',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showMessage(data.message, 'info');
            loadEvents();
            updateUserPointsDisplay();
        }
    })
    .catch(error => {
        console.error('Unregistration error:', error);
        showMessage('Unregistration failed. Please try again.', 'error');
    });
}

function markAttendance(eventId) {
    const formData = new FormData();
    formData.append('user_email', currentUser.email);
    
    fetch(`/events/${eventId}/mark-attendance`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showMessage(`${data.message} (+${data.points_earned} points!)`, 'success');
            updateUserPointsDisplay();
        } else if (data.detail) {
            showMessage(data.detail, 'error');
        }
    })
    .catch(error => {
        console.error('Attendance error:', error);
        showMessage('Failed to mark attendance. Please try again.', 'error');
    });
}

function completeEvent(eventId) {
    const formData = new FormData();
    formData.append('user_email', currentUser.email);
    
    fetch(`/events/${eventId}/complete`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showMessage(`${data.message} (+${data.points_earned} points!)`, 'success');
            updateUserPointsDisplay();
        } else if (data.detail) {
            showMessage(data.detail, 'error');
        }
    })
    .catch(error => {
        console.error('Complete event error:', error);
        showMessage('Failed to complete event. Please try again.', 'error');
    });
}

// Leaderboard Management
function loadLeaderboard() {
    fetch('/leaderboard?limit=50')
        .then(response => response.json())
        .then(data => {
            leaderboardData = data.leaderboard || [];
            displayLeaderboard(leaderboardData);
        })
        .catch(error => {
            console.error('Error loading leaderboard:', error);
            document.getElementById('leaderboard-list').innerHTML = '<p>Error loading leaderboard.</p>';
        });
}

function displayLeaderboard(leaderboard) {
    const leaderboardContainer = document.getElementById('leaderboard-list');
    
    if (leaderboard.length === 0) {
        leaderboardContainer.innerHTML = '<p>No leaderboard data available.</p>';
        return;
    }
    
    const leaderboardHTML = leaderboard.map(entry => {
        const rankClass = entry.rank <= 3 ? `rank-${entry.rank}` : 'rank-other';
        const isCurrentUser = entry.user_email === currentUser.email;
        
        return `
            <div class="leaderboard-item ${isCurrentUser ? 'current-user' : ''}">
                <div class="rank-badge ${rankClass}">
                    ${entry.rank}
                </div>
                <div class="user-info">
                    <div class="user-name">
                        ${entry.user_name}
                        ${isCurrentUser ? '(You)' : ''}
                    </div>
                    <div class="user-stats">
                        ${entry.badges_count} badges • ${entry.recent_activity}
                    </div>
                </div>
                <div class="points-display">
                    ${entry.total_points} pts
                </div>
            </div>
        `;
    }).join('');
    
    leaderboardContainer.innerHTML = leaderboardHTML;
}

function refreshLeaderboard() {
    document.getElementById('leaderboard-list').innerHTML = '<p>Loading leaderboard...</p>';
    loadLeaderboard();
    showMessage('Leaderboard refreshed!', 'info');
}

// Badge Management
function loadBadges() {
    fetch('/badges')
        .then(response => response.json())
        .then(data => {
            const badges = data.badges || [];
            displayBadges(badges);
        })
        .catch(error => {
            console.error('Error loading badges:', error);
            document.getElementById('badges-list').innerHTML = '<p>Error loading badges.</p>';
        });
}

function displayBadges(badges) {
    const badgesContainer = document.getElementById('badges-list');
    
    if (badges.length === 0) {
        badgesContainer.innerHTML = '<p>No badges available.</p>';
        return;
    }
    
    const badgesHTML = `
        <div class="badges-grid">
            ${badges.map(badge => `
                <div class="badge-card">
                    <div class="badge-icon">🏆</div>
                    <div class="badge-name">${badge.name}</div>
                    <div class="badge-description">${badge.description}</div>
                    <div class="badge-requirements">Requirements: ${badge.requirements}</div>
                </div>
            `).join('')}
        </div>
    `;
    
    badgesContainer.innerHTML = badgesHTML;
}

// Profile Management
function loadUserProfile() {
    if (!currentUser.email) {
        document.getElementById('profile-content').innerHTML = '<p>Please set your user information in the Events tab first.</p>';
        return;
    }
    
    fetch('/leaderboard/user/' + encodeURIComponent(currentUser.email))
        .then(response => response.json())
        .then(data => {
            displayUserProfile(data);
        })
        .catch(error => {
            console.error('Error loading user profile:', error);
            document.getElementById('profile-content').innerHTML = '<p>Error loading profile. You may need to participate in some events first.</p>';
        });
}

function displayUserProfile(profileData) {
    const profileContainer = document.getElementById('profile-content');
    const { ranking, point_history, badges } = profileData;
    
    const profileHTML = `
        <div class="profile-overview">
            <h4>📊 Your Statistics</h4>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${ranking.total_points}</div>
                    <div class="stat-label">Total Points</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">#${ranking.rank}</div>
                    <div class="stat-label">Current Rank</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${ranking.badges_count}</div>
                    <div class="stat-label">Badges Earned</div>
                </div>
            </div>
        </div>
        
        <div class="point-history">
            <h4>🏆 Recent Point History</h4>
            ${point_history.length > 0 ? point_history.map(record => `
                <div class="point-record">
                    <span class="points-earned">+${record.points_earned}</span>
                    <span class="point-reason">${record.reason}</span>
                    <span class="point-date">${new Date(record.date_awarded).toLocaleDateString()}</span>
                </div>
            `).join('') : '<p>No point history available.</p>'}
        </div>
        
        <div class="user-badges">
            <h4>🎖️ Your Badges</h4>
            ${badges.length > 0 ? `
                <div class="user-badges-grid">
                    ${badges.map(userBadge => `
                        <div class="user-badge-card earned">
                            <div class="badge-icon">🏆</div>
                            <div class="badge-name">${userBadge.badge.name}</div>
                            <div class="earned-date">Earned: ${new Date(userBadge.earned_date).toLocaleDateString()}</div>
                        </div>
                    `).join('')}
                </div>
            ` : '<p>No badges earned yet. Keep participating in events!</p>'}
        </div>
    `;
    
    profileContainer.innerHTML = profileHTML;
}

// Utility Functions
function showMessage(message, type = 'info') {
    const popup = document.getElementById('message-popup');
    const messageText = document.getElementById('message-text');
    
    messageText.textContent = message;
    popup.className = type;
    popup.classList.remove('hidden');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideMessage();
    }, 5000);
}

function hideMessage() {
    document.getElementById('message-popup').classList.add('hidden');
}

// Additional CSS for profile stats
const additionalCSS = `
    .profile-overview {
        margin-bottom: 2rem;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .stat-card {
        background: var(--primary-color);
        color: white;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        text-align: center;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .point-record {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        background: #f8f9fa;
        border-radius: var(--border-radius);
    }
    
    .points-earned {
        background: var(--success-color);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
    }
    
    .user-badges-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .current-user {
        border: 2px solid var(--secondary-color);
        background: rgba(255, 193, 7, 0.1);
    }
`;

// Add additional CSS to the document
const style = document.createElement('style');
style.textContent = additionalCSS;
document.head.appendChild(style);
