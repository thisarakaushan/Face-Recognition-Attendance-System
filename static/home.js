document.addEventListener("DOMContentLoaded", function () {
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

  mobileMenuToggle.addEventListener('click', function() {
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