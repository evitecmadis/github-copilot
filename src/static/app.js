document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const deregisterActivitySelect = document.getElementById("deregister-activity");
  const signupForm = document.getElementById("signup-form");
  const deregisterForm = document.getElementById("deregister-form");
  const messageDiv = document.getElementById("message");
  const deregisterMessageDiv = document.getElementById("deregister-message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Clear dropdown options (keep the placeholder)
      while (activitySelect.options.length > 1) {
        activitySelect.remove(1);
      }
      while (deregisterActivitySelect.options.length > 1) {
        deregisterActivitySelect.remove(1);
      }

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        const participantsList = details.participants
          .map(p => `<li>${p}</li>`)
          .join("");

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <p><strong>Participants:</strong></p>
          <ul class="participants-list">
            ${participantsList}
          </ul>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);

        // Add option to deregister dropdown
        const deregisterOption = document.createElement("option");
        deregisterOption.value = name;
        deregisterOption.textContent = name;
        deregisterActivitySelect.appendChild(deregisterOption);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle signup form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Handle deregister form submission
  deregisterForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("deregister-email").value;
    const activity = document.getElementById("deregister-activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/deregister?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        deregisterMessageDiv.textContent = result.message;
        deregisterMessageDiv.className = "success";
        deregisterForm.reset();
        fetchActivities();
      } else {
        deregisterMessageDiv.textContent = result.detail || "An error occurred";
        deregisterMessageDiv.className = "error";
      }

      deregisterMessageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        deregisterMessageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      deregisterMessageDiv.textContent = "Failed to deregister. Please try again.";
      deregisterMessageDiv.className = "error";
      deregisterMessageDiv.classList.remove("hidden");
      console.error("Error deregistering:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
