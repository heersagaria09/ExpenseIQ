// ===== Animation Utilities =====

class SmoothAnimations {
  
  // Accordion toggle with smooth animation
  static toggleAccordion(triggerId, contentId) {
    const trigger = document.getElementById(triggerId);
    const content = document.getElementById(contentId);
    
    if (!trigger || !content) return;
    
    const isOpen = content.classList.contains('open');
    
    if (isOpen) {
      // Closing
      content.style.maxHeight = content.scrollHeight + 'px';
      setTimeout(() => {
        content.classList.remove('open');
        content.style.maxHeight = '0px';
        trigger.classList.remove('expanded');
      }, 10);
    } else {
      // Opening
      content.classList.add('open');
      content.style.maxHeight = content.scrollHeight + 'px';
      trigger.classList.add('expanded');
      
      // Reset max-height after animation
      setTimeout(() => {
        content.style.maxHeight = 'none';
      }, 400);
    }
  }
  
  // Section switching with fade transition
  static switchSection(activeId, allSectionClass = 'content-section') {
    // Hide all sections
    document.querySelectorAll(`.${allSectionClass}`).forEach(section => {
      section.classList.add('hidden');
      section.classList.remove('active');
    });
    
    // Show target section after brief delay
    setTimeout(() => {
      const targetSection = document.getElementById(activeId);
      if (targetSection) {
        targetSection.classList.remove('hidden');
        targetSection.classList.add('active');
      }
    }, 150);
  }
  
  // Add message with smooth animation
  static addMessage(container, messageHTML, className = 'message-item') {
    const messageDiv = document.createElement('div');
    messageDiv.className = className;
    messageDiv.innerHTML = messageHTML;
    
    container.appendChild(messageDiv);
    
    // Trigger animation
    requestAnimationFrame(() => {
      messageDiv.classList.add('show');
    });
    
    // Scroll to bottom if container is scrollable
    if (container.scrollTop !== undefined) {
      container.scrollTop = container.scrollHeight;
    }
  }
  
  // Loading state toggle
  static setLoading(element, isLoading = true) {
    if (isLoading) {
      element.classList.add('loading-fade');
      element.style.pointerEvents = 'none';
    } else {
      element.classList.remove('loading-fade');
      element.style.pointerEvents = 'auto';
    }
  }
  
  // Fade transition between elements
  static fadeTransition(fromElement, toElement, duration = 300) {
    fromElement.style.transition = `opacity ${duration}ms ease`;
    fromElement.style.opacity = '0';
    
    setTimeout(() => {
      fromElement.style.display = 'none';
      toElement.style.display = 'block';
      toElement.style.opacity = '0';
      toElement.style.transition = `opacity ${duration}ms ease`;
      
      requestAnimationFrame(() => {
        toElement.style.opacity = '1';
      });
    }, duration);
  }
  
  // Smooth height transition
  static smoothHeight(element, targetHeight = 'auto') {
    const currentHeight = element.scrollHeight;
    element.style.height = currentHeight + 'px';
    element.style.transition = 'height 0.3s ease';
    
    requestAnimationFrame(() => {
      if (targetHeight === 'auto') {
        element.style.height = element.scrollHeight + 'px';
        setTimeout(() => {
          element.style.height = 'auto';
          element.style.transition = '';
        }, 300);
      } else {
        element.style.height = targetHeight;
      }
    });
  }
}

// Global animation utility functions
window.smoothToggle = (triggerId, contentId) => {
  SmoothAnimations.toggleAccordion(triggerId, contentId);
};

window.smoothSwitch = (activeId, allSectionClass) => {
  SmoothAnimations.switchSection(activeId, allSectionClass);
};

window.smoothMessage = (container, messageHTML, className) => {
  SmoothAnimations.addMessage(container, messageHTML, className);
};

// Initialize smooth animations on DOM load
document.addEventListener('DOMContentLoaded', () => {
  // Add smooth scroll class to html
  document.documentElement.classList.add('smooth-scroll');
  
  // Add animation container class to main content areas
  document.querySelectorAll('.section-card, .content-grid').forEach(el => {
    el.classList.add('animation-container');
  });
});