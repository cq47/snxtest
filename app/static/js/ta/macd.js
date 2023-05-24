// MACD
function ta_MACD(src, ma_type, fast_len, slow_len, sig_len) {
    fast_ma = ma_type == "sma" ? ta_SMA(src, fast_len) : ta_EMA(src, fast_len);
    slow_ma = ma_type == "sma" ? ta_SMA(src, slow_len) : ta_EMA(src, slow_len);
    macd = ta_ARR_DIFF(fast_ma, slow_ma);
    sig = ma_type == "sma" ? ta_SMA(macd, sig_len) : ta_EMA(macd, sig_len);
    hist = ta_ARR_DIFF(macd, sig);
    hist[0].color = '#eeeeee';
    for (i = 1; i < hist.length; i++) {
        if (hist[i].value >= 0) {
            hist[i].color = (hist[i - 1].value < hist[i].value) ? '#45CB85' : '#eeeeee';
        } else {
            hist[i].color = (hist[i - 1].value < hist[i].value) ? '#eeeeee' : '#F45B69';
        }
    }
    return [hist, macd, sig];
}

// Draws MACD
function st_MACD(chart, src, src_type, ma_type, fast_len, slow_len, signal_len, k=1, visible=true, fill_last_inps=false) {
    src_ = [];
    for (i = 0; i < src.length; i++) {
        src_.push({time: src[i].time, value: src[i][src_type]});
    }
    arr = ta_MACD(src_, ma_type, fast_len, slow_len, signal_len);

    series_list = [];

    a = chart.addHistogramSeries()

    s_hist = chart.addHistogramSeries({
        visible: visible,
        crosshairMarkerVisible: false,
        lastValueVisible: false,
        priceLineVisible: false,
        priceScaleId: 'macd',
        priceFormat: {type: 'price', precision: k, minMove: Math.pow(10, -k)}
    });

    s_hist.setData(arr[0]);
    series_list.push(s_hist);

    s_macd = chart.addLineSeries({
        color: '#35A7FF', 
        crosshairMarkerVisible: true,
        lastValueVisible: true,
        priceLineVisible: true,
        visible: visible,
        priceScaleId: 'macd',
        priceFormat: {type: 'price', precision: k, minMove: Math.pow(10, -k)}
    });
    s_macd.setData(arr[1]);
    series_list.push(s_macd);

    s_sig = chart.addLineSeries({
        color: '#EA7317', 
        crosshairMarkerVisible: false,
        lastValueVisible: false,
        priceLineVisible: false,
        visible: visible,
        priceScaleId: 'macd',
        priceFormat: {type: 'price', precision: k, minMove: Math.pow(10, -k)}
    });
    s_sig.setData(arr[2]);
    series_list.push(s_sig);

    // Add to indicators' tooltip
    if ($('.ind-tooltip div[ind="ind-macd"]').length == 0) {
        h = '<div ind="ind-macd" class="fr jb"><div class="mr20" style="color: var(--blue)">MACD</div><div>-</div></div>';
        $('.ind-tooltip > div').append(h);
    }

    // Prefill last inps html
    if (fill_last_inps) {
        $('#ind-macd .last-inps').html($('#ind-macd .inps').html());
    }

    return series_list;
}

// Called when Save button of indicator's settings is clicked
function st_MACD_save(this_, chart, chart_series_list) {
    k = 1;
    if (String(price_data[0].close).includes('.')) {
        k = String(price_data[0].close).split('.')[1].length;
    }

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
    ma_type = $(this_).closest('.inputs').find('.inps select[name="type"] option:selected').attr('value');
    fast_len = parseInt($(this_).closest('.inputs').find('.inps input[name="fast_len"]').val());
    slow_len = parseInt($(this_).closest('.inputs').find('.inps input[name="slow_len"]').val());
    sig_len = parseInt($(this_).closest('.inputs').find('.inps input[name="sig_len"]').val());

    // Create new ribbon
    vis = $(this_).closest('.ind').find('span .visibility').hasClass('yes');
    chart_series_list['data'] = st_MACD(chart, price_data, src_type, ma_type, fast_len, slow_len, sig_len, k, visible=vis);
    // Hide popup
    $(this_).closest('.inputs').addClass('op0');
    //
    $(this_).closest('.inputs').find('.last-inps').html($(this_).closest('.inputs').find('.inps').html());
    //
    resizePriceScales(chart);
}

// Initialize MACD (when we add a new indicator)
function init_MACD(use_last=false) {
    k = 1;
    if (String(price_data[0].close).includes('.')) {
        k = String(price_data[0].close).split('.')[1].length;
    }
    sel = 'inps';
    if (use_last) {
        sel = 'last-inps';
    }
    fast_len = parseInt($('#ind-macd .' + sel + ' input[name="fast_len"]').val());
    slow_len = parseInt($('#ind-macd .' + sel + ' input[name="slow_len"]').val());
    sig_len = parseInt($('#ind-macd .' + sel + ' input[name="sig_len"]').val());
    source = $('#ind-macd .' + sel + ' select[name="source"] option:selected').attr('value');
    ma_type = $('#ind-macd .' + sel + ' select[name="type"] option:selected').attr('value');
    // Check if we reload visible or hidden
    vis_ = true;
    visel = $('#ind-macd .visibility');
    if (visel.length > 0) {
        if (!$(visel).hasClass('yes')) {
            vis_ = false;
        }
    }
    return {'data': st_MACD(chart, price_data, source, ma_type, fast_len, slow_len, sig_len, k=k, visible=vis_, fill_last_inps=true)};
}