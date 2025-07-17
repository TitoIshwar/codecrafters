const badgeCounts = {
  Diamond: 4,
  Gold: 7,
  Silver: 10,
  Bronze: 15,
  Streak: 5,
  Freeze: 3
};

// Example: total 10 tasks, 7 completed
const TOTAL_TASKS = 10;
const COMPLETED_TASKS = 7;

function updateProgress() {
  const percent = Math.round((COMPLETED_TASKS / TOTAL_TASKS) * 100);
  document.getElementById('progressFill').style.height = `${percent}%`;
  document.getElementById('progressText').textContent = `${percent}%`;
}

function showBadge(type) {
  const popup = document.getElementById('popup');
  const popupText = document.getElementById('popup-text');
  popupText.innerHTML = `<strong>${type}</strong><br>You have earned <strong>${badgeCounts[type]}</strong>!`;
  popup.style.display = 'flex';
}

function closePopup() {
  document.getElementById('popup').style.display = 'none';
}

// Init

updateProgress();
  // Optional: Click outside to close
document.addEventListener("click", function(event) {
    const sidebar = document.getElementById("sidebar");
    const profileIcon = document.querySelector(".profile-icon");

    if (!sidebar.contains(event.target) && !profileIcon.contains(event.target)) {
      sidebar.classList.remove("active");
    }
  });
