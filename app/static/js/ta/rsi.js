// Calculate RSI
function ta_RSI(src, len) {
    res_ = [{time: src[0].time}];
    per = 1.0 / len;
    avg_gain = 0.0;
    avg_loss = 0.0;
    for (i = 1; i <= len; i++) {
        change = src[i].value - src[i - 1].value;
        gain = change > 0 ? change : 0;
        loss = change < 0 ? Math.abs(change) : 0;
        avg_gain += gain;
        avg_loss += loss;
        res_.push({time: src[i].time});
    }

    avg_gain = avg_gain / len;
    avg_loss = avg_loss / len;

    rsi_ = 100 * (avg_gain / (avg_gain + avg_loss));
    res_.push({time: src[i].time, value: rsi_});

    for (i = len + 1; i < src.length; i++) {
        change = src[i].value - src[i - 1].value;
        gain = change > 0 ? change : 0;
        loss = change < 0 ? Math.abs(change) : 0;
        avg_gain = (gain - avg_gain) * per + avg_gain;
        avg_loss = (loss - avg_loss) * per + avg_loss;
        rsi_ = 100 * (avg_gain / (avg_gain + avg_loss));
        res_.push({time: src[i].time, value: rsi_});
    }

    return res_;
}

// Draws RSI
function st_RSI(chart, src, src_type, len, visible=true, fill_last_inps=false) {
    src_ = [];
    for (i = 0; i < src.length; i++) {
        src_.push({time: src[i].time, value: src[i][src_type]});
    }
    rsi_ = ta_RSI(src_, len);
    series = chart.addLineSeries({
        color: '#9191E9', 
        crosshairMarkerVisible: true,
        lastValueVisible: true,
        priceLineVisible: true,
        visible: visible,
        priceScaleId: 'rsi'
    });
    series.setData(rsi_);

    // Add to indicators' tooltip
    if ($('.ind-tooltip div[ind="ind-rsi"]').length == 0) {
        h = '<div ind="ind-rsi" class="fr jb"><div class="mr20" style="color: var(--blue)">RSI</div><div>-</div></div>';
        $('.ind-tooltip > div').append(h);
    }

    // Prefill last inps html
    if (fill_last_inps) {
        $('#ind-rsi .last-inps').html($('#ind-rsi .inps').html());
    }

    return [series];
}

// Called when Save button of indicator's settings is clicked
function st_RSI_save(this_, chart, chart_series_list) {
    // Set inputs' value attribute
    $(this_).closest('.inputs').find('.inps input').each(function(i, el) {
        $(el).attr('value', $(el).val());
    })
    $(this_).closest('.inputs').find('.inps select option:selected').each(function(i, el) {
        $(el).parent().find('option').removeAttr('selected');
        $(el).attr('selected', 'selected');
    })
    // Remove old drawings 
    for (const cs of chart_series_list['data']) {
        chart.removeSeries(cs);
    }
    // Gather inputs
    src_type = $(this_).closest('.inputs').find('.inps select[name="source"] option:selected').attr('value');
    length = parseInt($(this_).closest('.inputs').find('.inps input').val());
    // Create new ribbon
    vis = $(this_).closest('.ind').find('span .visibility').hasClass('yes');
    chart_series_list['data'] = st_RSI(chart, price_data, src_type, length, visible=vis);
    // Hide popup
    $(this_).closest('.inputs').addClass('op0');
    //
    $(this_).closest('.inputs').find('.last-inps').html($(this_).closest('.inputs').find('.inps').html());
    //
    resizePriceScales(chart);
}

// Init
function init_RSI(use_last=false) {
    k = 1;
    if (String(price_data[0].close).includes('.')) {
        k = String(price_data[0].close).split('.')[1].length;
    }
    sel = 'inps';
    if (use_last) {
        sel = 'last-inps';
    }
    period = parseInt($('#ind-rsi .' + sel + ' input').val());
    source = $('#ind-rsi .' + sel + ' select option:selected').attr('value');
    // Check if we reload visible or hidden
    vis_ = true;
    visel = $('#ind-rsi .visibility');
    if (visel.length > 0) {
        if (!$(visel).hasClass('yes')) {
            vis_ = false;
        }
    }
    return {'data': st_RSI(chart, price_data, source, period, vis_, fill_last_inps=true)};
}