console.log("JS connected to", document.title);

// -------------------- CALENDAR LOGIC (Only for streak calendar page) --------------------

const calendarGrid = document.getElementById("calendarGrid");
const monthYear = document.getElementById("monthYear");

let currentDate = new Date();
let taskData = {}; // Simulated task results (to be replaced with Supabase later)

function generateMockData(month, year) {
  taskData = {};
  const totalDays = new Date(year, month + 1, 0).getDate();
  for (let i = 1; i <= totalDays; i++) {
    const rand = Math.random();
    if (rand < 0.3) taskData[i] = "not-completed";
    else if (rand < 0.6) taskData[i] = "completed";
    else if (rand < 0.85) taskData[i] = "streak";
    else taskData[i] = ""; // No task
  }
}

function renderCalendar(date) {
  if (!calendarGrid || !monthYear) return; // ✅ Only run if elements exist

  const year = date.getFullYear();
  const month = date.getMonth();
  generateMockData(month, year);

  monthYear.textContent = `${date.toLocaleString("default", {
    month: "long",
  })} ${year}`;
  calendarGrid.innerHTML = "";

  const firstDay = new Date(year, month, 1).getDay();
  const totalDays = new Date(year, month + 1, 0).getDate();

  for (let i = 0; i < firstDay; i++) {
    const blank = document.createElement("div");
    calendarGrid.appendChild(blank);
  }

  for (let i = 1; i <= totalDays; i++) {
    const dayDiv = document.createElement("div");
    dayDiv.classList.add("day");

    if (
      i === new Date().getDate() &&
      month === new Date().getMonth() &&
      year === new Date().getFullYear()
    ) {
      dayDiv.classList.add("today");
    }

    const status = taskData[i];
    if (status) {
      dayDiv.classList.add(status);
    }

    dayDiv.textContent = i;
    calendarGrid.appendChild(dayDiv);
  }
}

function changeMonth(offset) {
  if (!calendarGrid) return;
  currentDate.setMonth(currentDate.getMonth() + offset);
  renderCalendar(currentDate);
}

// Run calendar only if on calendar page
if (calendarGrid && monthYear) {
  renderCalendar(currentDate);
}

// -------------------- SIDEBAR TOGGLE LOGIC (Optional) --------------------

function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (sidebar) {
    sidebar.classList.toggle("active");
  }
}

document.addEventListener("click", function (event) {
  const sidebar = document.getElementById("sidebar");
  const profileIcon = document.querySelector(".profile-icon");

  if (
    sidebar &&
    profileIcon &&
    !sidebar.contains(event.target) &&
    !profileIcon.contains(event.target)
  ) {
    sidebar.classList.remove("active");
  }
});

// -------------------- FEEDBACK 1 (Emotion Selection) --------------------

document.addEventListener("DOMContentLoaded", () => {
  const emojiButtons = document.querySelectorAll(".emotion-btn");
  const submitBtn = document.getElementById("submitBtn");

  if (emojiButtons.length && submitBtn) {
    let selectedEmotion = null;

    emojiButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        emojiButtons.forEach((b) => b.classList.remove("selected"));
        btn.classList.add("selected");
        selectedEmotion = btn.dataset.emoji;
      });
    });

    submitBtn.addEventListener("click", () => {
      if (!selectedEmotion) {
        alert("Please select an emotion first!");
        return;
      }
      console.log("Selected Emotion:", selectedEmotion);
      window.location.href = "feedback2.html";
    });
  }
});

// -------------------- FEEDBACK 2 (Reflection Submit) --------------------

function submitReflection() {
  const reflectionBox = document.getElementById("reflection");
  if (!reflectionBox) return;

  const reflection = reflectionBox.value.trim();

  if (reflection === "") {
    alert("Please write something before submitting.");
    return;
  }

  console.log("Reflection Submitted:", reflection);
  alert("Thanks for your feedback!");
  window.location.href = "home.html"; // Redirect to home
}
