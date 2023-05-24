// Setup width of select based on selected option's contents
function setupSelectWidth(this_) {
    // Get text of selected option
    t = $(this_).find('option:selected').text();
    // Add fake option
    tempOption = document.createElement('option');
    tempOption.textContent = t;
    // Add fake select
    tempSelect = document.createElement('select');
    tempSelect.style.visibility = "hidden";
    tempSelect.style.position = "fixed"
    tempSelect.appendChild(tempOption);
    $(this_).parent().append(tempSelect);
    // Apply width
    $(this_).css('width', String(tempSelect.clientWidth + 15) + 'px');
    tempSelect.remove();
    tempOption.remove();
}

// Show assets based on inputs
function showAssets(pre=true) {
    if (pre) {
        val1 = $('select[name="blue-type"] option:selected').attr('value');
        val2 = $('.input-select').next('div').find('div.active').attr('data-type');
        if (val1 == undefined && val2 == undefined) {
            val1 = $('.row-ui .type > div.active').attr('data-type');
            val2 = 'all';
        }
        $('.row-ui > div:last-child > div').addClass('op0');
        el = $('#group-' + val1 + '-' + val2);
        if (el.length > 0) {
            el.removeClass('op0');
            $('.nodata-found').addClass('op0');
        } else {
            $('.nodata-found').removeClass('op0');
        }
    }
    // Show / hide the "more" arrow
    h = 0;
    $('.row-ui > div > div > .row:not(.op0)').each(function(i, el) {
        h += el.offsetHeight;
    });
    
    harea = $('.row-ui > div:last-child').height();
    if (h > harea) {
        $('.icon-more').removeClass('op0');
    } else {
        $('.icon-more').addClass('op0');
    }
    // Scroll to top
    $('.scroller').animate({scrollTop: 0}, 200, 'swing');
}
