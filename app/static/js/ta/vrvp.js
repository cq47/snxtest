// Calculates volume profile
function ta_VRVP(start_bi, end_bi, highest, lowest, row_num) {
    low_list = [];
    high_list = [];
    price_list = [];
    buy_vol_list = [];
    sell_vol_list = [];

    height_ = (highest - lowest) / row_num;

    for (ii7 = 0; ii7 < row_num; ii7++) {
        l_ = lowest + height_ * ii7;
        h_ = lowest + height_ * (ii7 + 1);
        low_list.push(l_);
        high_list.push(h_);
        price_list.push((h_ + l_) / 2);
        buy_vol_list.push(0);
        sell_vol_list.push(0);
    }

    // Find volumes per histogram bar
    for (ii7 = start_bi; ii7 < end_bi; ii7++) {
        d_ = price_data[ii7];
        vol__ = d_.volume;
        clo_ = d_.close;
        hi_ = d_.high;
        lo_ = d_.low;
        // Current bar height
        cur_bh = d_.high - d_.low;
        // Calculate current buy and sell volume
        buyVol = vol__ * (clo_ - lo_);
        sellVol = vol__ * (hi_ - clo_);
        // 
        for (ii8 = 0; ii8 < row_num; ii8++) {
            h_ = high_list[ii8];
            l_ = low_list[ii8];
            target = Math.max(h_, hi_) - Math.min(l_, lo_) - (Math.max(h_, hi_) - Math.min(h_, hi_)) - (Math.max(l_, lo_) - Math.min(l_, lo_));
            vol_perc = target / cur_bh;
            if (vol_perc > 0) {
                buy_vol_list[ii8] += buyVol * vol_perc;
                sell_vol_list[ii8] += sellVol * vol_perc;
            } 
        }
    }
    // 
    return {buy: buy_vol_list, sell: sell_vol_list};
}

// Called when Save button of indicator's settings is clicked
function st_VRVP_save(this_, chart) {
    // Set inputs' value attribute
    $(this_).closest('.inputs').find('.inps input').each(function(i, el) {
        $(el).attr('value', $(el).val());
    })
    $(this_).closest('.inputs').find('.inps select option:selected').each(function(i, el) {
        $(el).parent().find('option').removeAttr('selected');
        $(el).attr('selected', 'selected');
    })
    // Gather inputs
    vrvp_type_ = $(this_).closest('.inputs').find('.inps select[name="type"] option:selected').attr('value');
    nrows_ = parseInt($(this_).closest('.inputs').find('.inps input[name="nrows"]').val());
    width_ = parseInt($(this_).closest('.inputs').find('.inps input[name="width"]').val());
    // Change parameters
    window.vrvp_type = vrvp_type_;
    window.vrvp_nrows = nrows_;
    window.vrvp_width = width_;
    // Hide popup
    $(this_).closest('.inputs').addClass('op0');
    $(this_).closest('.inputs').find('.last-inps').html($(this_).closest('.inputs').find('.inps').html());
    //
    resizePriceScales(chart);
}

// Init
function init_VRVP() {
    $('#ind-vrvp .last-inps').html($('#ind-vrvp .inps').html());
    window.vrvp_nrows = 20;
    window.vrvp_type = 'bs';
    window.vrvp_width = 25;
    window.vrvp_px_data = [];
    window.vrvp_visible = true;
    return {data: []};
}