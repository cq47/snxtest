// Draws MA ribbon
function st_MA_Ribbon(chart, src, ma_types, src_types, periods, visible=true, fill_last_inps=false) {
    // Will store series data
    res = [];
    // Sort in ascending order
    arr_ = [];
    for (i = 0; i < periods.length; i++) {
        arr_.push({period: periods[i], ma_type: ma_types[i], src_type: src_types[i], index: i})
    }
    arr_ = arr_.sort((a, b) => a.period - b.period);
    // Counter for color's transparency
    counter = 0;
    // Add MA one by one
    for (const el of arr_) {
        period = parseInt(el.period);
        ma_type = el.ma_type;
        src_type = el.src_type;
        // Get source based on src_type
        src_ = [];
        for (i = 0; i < src.length; i++) {
            src_.push({time: src[i]['time'], value: src[i][src_type]});
        }
        // Calculate transparency for line
        tr = Math.round(255 - 150 / arr_.length * counter).toString(16);
        series = chart.addLineSeries({
            color: (ma_type == "sma" ? "#F45B69" : "#5C7AFF") + tr, 
            crosshairMarkerVisible: false,
            lastValueVisible: false,
            priceLineVisible: false,
            visible: visible,
            priceScaleId: 'right'
        });
        series.cid = el.index;
        ma = ma_type == "sma" ? ta_SMA(src_, period) : ta_EMA(src_, period);
        series.setData(ma);
        res.push(series);
        counter += 1;
    }
    
    // Add items to indicators' tooltip
    if ($('.ind-tooltip div[ind="ind-ma-ribbon"]').length > 0) {
        $('.ind-tooltip div[ind="ind-ma-ribbon"]').remove();
    } 
    h = '<div ind="ind-ma-ribbon" class="fr jb"><div class="mr20" style="color: var(--blue)">MA Ribbon:</div></div>';
    $('.ind-tooltip > div').append(h);
    counter = 1;
    for (i = 0; i < arr_.length; i++) {
        for (const el of arr_) {
            if (el.index == i) {
                h = '<div ind="ind-ma-ribbon" index="' + el.index + '" class="fr jb"><div class="mr20" style="color: var(--blue); margin-left: 20px">- MA №' + String(i + 1) + '</div><div>-</div></div>';
                $('.ind-tooltip > div').append(h);
                break;
            }
        }
    }
    // Prefill last inps html
    if (fill_last_inps) {
        $('#ind-ma-ribbon .last-inps').html($('#ind-ma-ribbon .inps').html());
    }
    // Return
    return res;
}

// Called when "New period" is clicked
function st_MA_Ribbon_add(this_) {
    n = String($(this_).parent().parent().find('.inps .period:not(.op0)').length + 1);
    h = '<div class="fr jb mt20 period"><div class="title" style="margin-top: 9px; white-space: nowrap">MA №' + n + '</div><div class="fr ml20"><select name="type" class="mr20"><option value="sma">SMA</option><option value="ema">EMA</option></select><select name="source" class="mr20"><option value="open">Open</option><option value="high">High</option><option value="low">Low</option><option selected value="close">Close</option></select><input type="number" value="5"><div class="remove ml20"><img onclick="st_MA_Ribbon_remove_row(this)" class="cf-red" src="/static/icons/cross.png" width="20" height="20" style="cursor: pointer; margin-top: 9px"></div></div></div>';
    $(this_).closest('.inputs').find('.inps').append(h);
    $(this_).parent().parent().find('.inps .period .remove').removeClass('op0');
}

// Called when Save button of indicator's settings is clicked
function st_MA_Ribbon_save(this_, chart, chart_series_list) {
    // Set inputs' value attribute
    $(this_).closest('.inputs').find('.inps input').each(function(i, el) {
        $(el).attr('value', $(el).val());
    })
    $(this_).closest('.inputs').find('.inps select option:selected').each(function(i, el) {
        $(el).parent().find('option').removeAttr('selected');
        $(el).attr('selected', 'selected');
    })
    // Remove hidden period rows
    $(this_).parent().parent().find('.inps .period.op0').remove();
    // Gather periods
    periods = [];
    src_types = [];
    ma_types = [];
    $(this_).closest('.inputs').find('.inps .period input').each(function(i, el) {
        periods.push(parseInt($(el).val()));
        src_types.push($(el).parent().find('select[name="source"] option:selected').attr('value'));
        ma_types.push($(el).parent().find('select[name="type"] option:selected').attr('value'));
    })
    // Remove old drawings 
    for (const cs of chart_series_list['data']) {
        chart.removeSeries(cs);
    }
    // Create new ribbon
    vis = $(this_).closest('.ind').find('span .visibility').hasClass('yes');
    chart_series_list['data'] = st_MA_Ribbon(chart, price_data, ma_types, src_types, periods, visible=vis);
    // Hide popup
    $(this_).closest('.inputs').addClass('op0');
    // 
    $(this_).closest('.inputs').find('.last-inps').html($(this_).closest('.inputs').find('.inps').html());
    //
    resizePriceScales(chart);
}

// Called when we remove MA row 
function st_MA_Ribbon_remove_row(this_) {
    par = $(this_).parent().parent().parent().parent();
    if (par.find('.period').length > 1) {
        $(this_).parent().parent().parent().addClass('op0');
        if (par.find('.period:not(.op0)').length == 1) {
            par.find('.period:not(.op0) .remove').addClass('op0');
        } else {
            par.find('.period:not(.op0) .remove').removeClass('op0');
        }
        $(par).find('.period:not(.op0)').each(function(i, el) {
            $(el).find('.title').text('MA №' + String(i + 1));
        })
    } 
}

// Init 
function init_MA_Ribbon(use_last=false) {
    k = 1;
    if (String(price_data[0].close).includes('.')) {
        k = String(price_data[0].close).split('.')[1].length;
    }
    periods_sma = [];
    ma_types = [];
    src_types = [];
    sel = 'inps';
    if (use_last) {
        sel = 'last-inps';
    }
    $('#ind-ma-ribbon .' + sel + ' .period input').each(function(i, el) {
        periods_sma.push(parseInt($(el).val()));
        ma_types.push($(el).parent().find('select[name="type"] option:selected').attr('value'));
        src_types.push($(el).parent().find('select[name="source"] option:selected').attr('value'));
    })
    // Check if we reload visible or hidden
    vis_ = true;
    visel = $('#ind-ma-ribbon .visibility');
    if (visel.length > 0) {
        if (!$(visel).hasClass('yes')) {
            vis_ = false;
        }
    }
    return {'data': st_MA_Ribbon(chart, price_data, ma_types, src_types, periods_sma, vis_, fill_last_inps=!use_last)};
}