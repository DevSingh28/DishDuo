$(document).ready(function() {
    $('#searchForm').submit(function(event) {
        event.preventDefault(); // Prevent default form submission

        // Extract the search query from the input field
        var searchQuery = $('#searchInput').val();

        // Make an AJAX request to search for users
        $.ajax({
            url: '/search/users',
            method: 'GET',
            data: {query: searchQuery}, // Pass the search query as data
            success: function(response) {
                // Handle the successful response
                if (response.users.length > 0) {
                    // User(s) found, load the user profile
                    var userId = response.users[0].id; // Assuming you only want to load the profile of the first user
                    window.location.href = '/view_profile/' + userId; // Redirect to the user profile page
                } else {
                    // No user found, display a pop-up message
                    alert('No user found.');
                }
            },
            error: function(xhr, status, error) {
                // Handle errors if any
                console.error(error);
            }
        });
    });
});


    var typed = new Typed('#elementnino', {
        strings: ['Welcome to DishDuo:', 'Where Culinary Creations Meet Community'],
        typeSpeed: 50, // Adjust typing speed if needed
        loop: true,
        loopCount: Infinity,
        onComplete: function () {
            setTimeout(function () {
                typed.stop(); // Stop Typed.js instance after completion
                setTimeout(function() {
                    typed.start(); // Restart Typed.js instance after a delay
                }, 5000); // Delay for 5 seconds before restarting
            }, 0); // Wait for Typed.js instance to complete before stopping
        }
    });

  document.addEventListener('DOMContentLoaded', function () {
    document.body.addEventListener('mousemove', function (e) {
      const dot = document.createElement('div');
      dot.classList.add('green-dot');
      dot.style.position = 'fixed';
      dot.style.left = `${e.clientX}px`;
      dot.style.top = `${e.clientY}px`;
      document.body.appendChild(dot);
      setTimeout(() => {
        dot.style.transform = 'scale(0)';
      }, 100);
      setTimeout(() => {
        dot.remove();
      }, 1000);
    });
  });

    $(document).on('click', '.like-btn', function(e){
    e.preventDefault();
    var $this = $(this);
    $.ajax({
        url: $this.closest('form').attr('action'), // Adjusted to find the form closest to the button
        type: 'post',
        success: function(response){
            console.log(response);  // Log the response from the server
            if($this.hasClass('liked')){
                $this.removeClass('liked');
                $this.find('i').removeClass('bi-heart-fill').addClass('bi-heart');
                $this.find('i').removeClass('text-danger').addClass('text-secondary');
                $this.html('<i class="bi bi-heart text-secondary"></i>');
            } else {
                $this.addClass('liked');
                $this.find('i').removeClass('bi-heart').addClass('bi-heart-fill');
                $this.find('i').removeClass('text-secondary').addClass('text-danger');
                $this.html('<i class="bi bi-heart-fill text-danger"></i>');
            }
            var likeCountElement = $this.closest('.counter_98').find('.like-count');
            console.log(likeCountElement);  // Log the like-count element
            likeCountElement.text(response.new_like_count + ' Like');  // Update the like count
            console.log(likeCountElement.text());  // Log the new text of the like-count element
        }
    });
});

var loaded_posts = 0;
var posts_per_page = 10;

$('#load-more-button').click(function() {
    loaded_posts += posts_per_page;
    $.get('/?loaded_posts=' + loaded_posts, function(data) {
        $('#posts-container').append(data);
    });
});

