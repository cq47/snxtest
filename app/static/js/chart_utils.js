// When save chart button is clicked
function chartSave(asset_id, chart_tf) {
    $(this).addClass('loading');

    // Gather data for VRVP
    vrvp_data = {
        'on': $('#ind-vrvp').length == 1,
        'vis': $('#ind-vrvp .visibility').hasClass('yes'),
        'settings': {
            'nrows': $('#ind-vrvp .inputs .inps input[name="nrows"]').val(),
            'type': $('#ind-vrvp .inputs .inps select > option:selected').attr('value'),
            'width': $('#ind-vrvp .inputs .inps input[name="width"]').val()
        }
    }

    // Gather data for MA Ribbon
    ma_ribbon_data = {
        'on': $('#ind-ma-ribbon').length == 1,
        'vis': $('#ind-ma-ribbon .visibility').hasClass('yes'),
        'settings': []
    }
    $('#ind-ma-ribbon .inputs .inps .period').each(function(i, el) {
        ma_ribbon_data['settings'].push({
            'type': $(el).find('select[name="type"] > option:selected').attr('value'),
            'source': $(el).find('select[name="source"] > option:selected').attr('value'),
            'period': $(el).find('input').val()
        })
    })

    // Gather data for Volume
    vol_data = {
        'on': $('#ind-vol').length == 1,
        'vis': $('#ind-vol .visibility').hasClass('yes')
    }

    // Gather data for MACD
    macd_data = {
        'on': $('#ind-macd').length == 1,
        'vis': $('#ind-macd .visibility').hasClass('yes'),
        'settings': {
            'source': $('#ind-macd .inputs .inps select[name="source"] > option:selected').attr('value'),
            'type': $('#ind-macd .inputs .inps select[name="type"] > option:selected').attr('value'),
            'fast_len': $('#ind-macd .inputs .inps input[name="fast_len"]').val(),
            'slow_len': $('#ind-macd .inputs .inps input[name="slow_len"]').val(),
            'sig_len': $('#ind-macd .inputs .inps input[name="sig_len"]').val()
        }
    }

    // Gather data for RSI
    rsi_data = {
        'on': $('#ind-rsi').length == 1,
        'vis': $('#ind-rsi .visibility').hasClass('yes'),
        'settings': {
            'source': $('#ind-rsi .inputs .inps select[name="source"] > option:selected').attr('value'),
            'period': $('#ind-rsi .inputs .inps input').val()
        }
    }

    // All data
    data = {
        'indicators': {
            'vrvp': vrvp_data,
            'ma_ribbon': ma_ribbon_data,
            'vol': vol_data,
            'macd': macd_data,
            'rsi': rsi_data
        }, 'drawings': drawings
    }

    // Send request
    console.log('saving')
    $.ajax({
        url: '/api/chart/save',
        type: "POST",
        dataType: 'json',
        data: {
            'asset_id': asset_id,
            'chart_tf': chart_tf,
            'data': JSON.stringify(data)
        },
        success: (data) => {
            console.log(data);
        },
        error: (error) => {
            console.log(error);
        }
    });
}