document.addEventListener('DOMContentLoaded', function() {
    document.body.classList.add('enhanced-layout');
    
    initSidebar();
    initActiveStates();
});

function initSidebar() {
    const sidebar = document.querySelector('.enhanced-sidebar');
    const contentPage = document.querySelector('.enhanced-content');
    
    if (!sidebar || !contentPage) return;
    
    let hoverTimeout;
    
    sidebar.addEventListener('mouseenter', function() {
        clearTimeout(hoverTimeout);
        sidebar.classList.add('sidebar-expanded');
        contentPage.classList.add('content-shifted');
    });
    
    sidebar.addEventListener('mouseleave', function() {
        hoverTimeout = setTimeout(function() {
            sidebar.classList.remove('sidebar-expanded');
            contentPage.classList.remove('content-shifted');
        }, 300);
    });
    
    sidebar.addEventListener('click', function() {
        clearTimeout(hoverTimeout);
    });
}

function initActiveStates() {
    const currentPath = window.location.pathname;
    const menuLinks = document.querySelectorAll('.enhanced-sidebar .menu-link');
    
    menuLinks.forEach(function(link) {
        link.classList.remove('active');
    });
    
    let activeLinkFound = false;
    
    menuLinks.forEach(function(link) {
        const href = link.getAttribute('href');
        
        if (!href || href === '#' || href.startsWith('#')) {
            return;
        }
        
        if (href === currentPath) {
            link.classList.add('active');
            activeLinkFound = true;
            
            const parentSubmenu = link.closest('.nav-second-level');
            if (parentSubmenu) {
                const parentLink = parentSubmenu.previousElementSibling;
                if (parentLink) {
                    parentLink.setAttribute('aria-expanded', 'true');
                    parentLink.classList.add('active');
                }
            }
        }
        else if (currentPath.startsWith(href) && href !== '/' && href !== currentPath) {
            if (!activeLinkFound) {
                link.classList.add('active');
                activeLinkFound = true;
            }
        }
        
        if (link.hasAttribute('data-bs-toggle') && link.getAttribute('data-bs-toggle') === 'collapse') {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetCollapse = document.getElementById(targetId);
                
                if (targetCollapse) {
                    const isExpanded = link.getAttribute('aria-expanded') === 'true';
                    link.setAttribute('aria-expanded', !isExpanded);
                    
                    if (isExpanded) {
                        targetCollapse.classList.remove('show');
                    } else {
                        targetCollapse.classList.add('show');
                    }
                }
            });
        }
    });
    
    if (!activeLinkFound) {
        const submenuLinks = document.querySelectorAll('.enhanced-sidebar .nav-second-level a');
        submenuLinks.forEach(function(link) {
            const href = link.getAttribute('href');
            if (href && (currentPath === href || currentPath.startsWith(href + '/'))) {
                link.classList.add('active');
                const parentMenu = link.closest('.nav-second-level');
                if (parentMenu) {
                    const parentLink = parentMenu.previousElementSibling;
                    if (parentLink) {
                        parentLink.setAttribute('aria-expanded', 'true');
                        parentLink.classList.add('active');
                    }
                }
            }
        });
    }
}

window.addEventListener('resize', function() {
    const sidebar = document.querySelector('.enhanced-sidebar');
    
    if (window.innerWidth <= 768) {
        console.log('Mobile view - sidebar remains hover-controlled');
    }
});

window.EnhancedNavigation = {
    setActiveMenuItem: function(selector) {
        document.querySelectorAll('.enhanced-sidebar .menu-link').forEach(function(link) {
            link.classList.remove('active');
        });
        
        const activeItem = document.querySelector(selector);
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }
};