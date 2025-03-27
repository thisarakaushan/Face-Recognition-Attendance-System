document.addEventListener("DOMContentLoaded", function () {

  // Event listeners
  const buttons = document.querySelectorAll(".method-card button");
  buttons.forEach((button) => {
    button.addEventListener("click", function () {
      const method = this.textContent.trim();
      if (method === "Turn On Camera") {
        window.alert(
          "Please wait sometime for the Face Recognition Program to activate. It takes sometime. Please note that you have to press 'Esc' button to exit it."
        );

        // Send a request to the Flask API to run live_face_recognition_attendance.py
        runLiveFaceRecognition();
      } else if (method === "Upload an Image(s)") {
        window.alert(
          "Please wait sometime for the Face Recognition Program to activate. It takes sometime. Please note that you have to press 'Esc' button to exit it."
        );

        // Open file input dialog
        const fileInput = document.createElement("input");
        fileInput.type = "file";
        fileInput.id = "fileInput";
        fileInput.accept = "image/*";
        fileInput.multiple = true;
        fileInput.addEventListener("change", function (event) {
          const selectedFiles = event.target.files;
          // Send a request to the Flask API with the selected image
          runImageFaceRecognition(selectedFiles);
        });
        fileInput.click();
      }
    });
  });

  // Attendance records Checking
  const submitButton = document.querySelector(".btn-submit");
  submitButton.addEventListener("click", function () {
    const date = document.getElementById("datepicking").value;
    const fromTime = document.getElementById("fromtimepicking").value;
    const toTime = document.getElementById("totimepicking").value;
    // Send a request to the Flask API with date, from time, and to time parameters
    runAttendanceQuery(date, fromTime, toTime);
  });

  // // Time Picker with Enhanced OK Button
  // function enhanceTimePickers() {
  //   const timeInputs = document.querySelectorAll('input[type="time"]');

  //   timeInputs.forEach(input => {
  //     // Create OK button container
  //     const okButtonContainer = document.createElement('div');
  //     okButtonContainer.className = 'time-ok-container';

  //     // Create OK button
  //     const okButton = document.createElement('button');
  //     okButton.className = 'time-ok-btn';
  //     okButton.textContent = 'OK';
  //     okButton.type = 'button';

  //     // Add to container
  //     okButtonContainer.appendChild(okButton);
  //     input.parentNode.insertBefore(okButtonContainer, input.nextSibling);

  //     // Show/hide logic
  //     input.addEventListener('focus', function () {
  //       okButtonContainer.style.display = 'block';
  //     });

  //     input.addEventListener('blur', function () {
  //       // Small delay to allow OK button click to register
  //       setTimeout(() => {
  //         okButtonContainer.style.display = 'none';
  //       }, 200);
  //     });

  //     // OK button functionality
  //     okButton.addEventListener('click', function () {
  //       input.blur(); // Close the picker
  //       okButtonContainer.style.display = 'none';

  //       // Force update if needed (for some browsers)
  //       if (input.value) {
  //         const event = new Event('change');
  //         input.dispatchEvent(event);
  //       }
  //     });
  //   });
  // }

  // Functions (remain the same as before)
  function runLiveFaceRecognition() {
    fetch("http://localhost:5000/run_live_face_recognition", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => displayResult(data.results))
      .catch((error) => console.error("Error:", error));
  }

  function runImageFaceRecognition(imageFiles) {
    const formData = new FormData();
    for (const file of imageFiles) {
      formData.append("images[]", file);
    }

    fetch("http://localhost:5000/run_image_face_recognition", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => displayResult(data.results))
      .catch((error) => console.error("Error:", error));
  }

  function runAttendanceQuery(date, fromTime, toTime) {
    if (date == "" || fromTime == "" || toTime == "")
      window.alert("Please enter all the details");
    else {
      fetch(
        `http://localhost:5000/query_attendance?date=${date}&fromTime=${fromTime}&toTime=${toTime}`,
        {
          method: "GET",
        }
      )
        .then((response) => response.json())
        .then((data) => displayResult(data.results))
        .catch((error) => console.error("Error:", error));
    }
  }

  // Display results section
  function displayResult(results) {
    // Create results section if it doesn't exist
    let resultsSection = document.querySelector(".results-section");
    if (!resultsSection) {
      resultsSection = document.createElement("section");
      resultsSection.className = "results-section";

      const resultsDiv = document.createElement("div");
      resultsDiv.className = "results";
      resultsSection.appendChild(resultsDiv);

      // Insert after the attendance-check section
      const attendanceCheck = document.querySelector(".attendance-check");
      attendanceCheck.insertAdjacentElement("afterend", resultsSection);
    }

    const resultsContainer = resultsSection.querySelector(".results");
    resultsContainer.innerHTML = "";

    let counter = 0;
    const h3 = document.createElement("h3");
    const text = document.createTextNode("Students Attended");
    h3.appendChild(text);
    resultsContainer.appendChild(h3);

    results.forEach((result) => {
      const listItem = document.createElement("div");
      if (!(result == "No Students Found")) {
        listItem.textContent = counter + 1 + ") " + result;
        counter = counter + 1;
      } else {
        listItem.textContent = result;
      }
      resultsContainer.appendChild(listItem);
    });
  }

  // Mobile Menu Toggle
  const mobileMenuToggle = document.createElement('div');
  mobileMenuToggle.classList.add('mobile-menu-toggle');
  mobileMenuToggle.innerHTML = `
    <span></span>
    <span></span>
    <span></span>
  `;

  const navWrapper = document.querySelector('.nav-wrapper');
  navWrapper.insertBefore(mobileMenuToggle, navWrapper.querySelector('.nav-links'));

  mobileMenuToggle.addEventListener('click', function () {
    const navLinks = document.querySelector('.nav-links');
    navLinks.classList.toggle('active');

    // Toggle menu icon to close
    this.classList.toggle('active');
  });

  // Close mobile menu when a link is clicked
  const navLinks = document.querySelectorAll('.nav-links a');
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      document.querySelector('.nav-links').classList.remove('active');
      document.querySelector('.mobile-menu-toggle').classList.remove('active');
    });
  });

  // Clear button functionality in Attendance recording
  const clearButton = document.querySelector(".btn-clear");
  clearButton.addEventListener("click", function () {
    // Clear form inputs
    document.getElementById("datepicking").value = "";
    document.getElementById("fromtimepicking").value = "";
    document.getElementById("totimepicking").value = "";

    // Remove results section if it exists
    const resultsSection = document.querySelector(".results-section");
    if (resultsSection) {
      resultsSection.remove();
    }
  });

  // Update year in footer
  const yearElement = document.getElementById("year");
  if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
  } else {
    console.error("Could not find element with ID 'year'");
  }

  // Scroll to top button functionality
  const scrollToTopBtn = document.createElement('button');
  scrollToTopBtn.innerHTML = '&#9650;'; // Up arrow
  scrollToTopBtn.classList.add('scroll-to-top');
  document.body.appendChild(scrollToTopBtn);

  scrollToTopBtn.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  // Show/hide scroll to top button based on scroll position
  window.addEventListener('scroll', () => {
    if (window.pageYOffset > 300) {
      scrollToTopBtn.style.display = 'block';
    } else {
      scrollToTopBtn.style.display = 'none';
    }
  });
});