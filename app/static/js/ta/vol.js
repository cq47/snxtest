// Draws Volume histogram
function st_VOL(chart, src, visible=true) {
    src_ = [];
    for (i = 0; i < src.length; i++) {
        src_.push({time: src[i].time, value: src[i]['volume'], color: (src[i]['close'] >= src[i]['open']) ? '#45CB85' : '#F45B69'});
    }
    series = chart.addHistogramSeries({
        priceFormat: {
            type: 'volume',
        },
        visible: visible,
        crosshairMarkerVisible: true,
        lastValueVisible: true,
        priceLineVisible: true,
        priceScaleId: 'vol'
    });
    series.setData(src_);

    // Add to indicators' tooltip
    if ($('.ind-tooltip div[ind="ind-vol"]').length == 0) {
        h = '<div ind="ind-vol" class="fr jb"><div class="mr20" style="color: var(--blue)">Volume</div><div>-</div></div>';
        $('.ind-tooltip > div').append(h);
    }

    return [series];
}

function init_VOL() {
    // Check if we reload visible or hidden
    vis_ = true;
    visel = $('#ind-vol .visibility');
    if (visel.length > 0) {
        if (!$(visel).hasClass('yes')) {
            vis_ = false;
        }
    }
    return {'data': st_VOL(chart, price_data, vis_)};
}