// Calculates sum of src (array of prices)
function ta_SUM(src) {
    var res = 0.0;
    for (j = 0; j < src.length; j++) {
        res += src[j].value;
    }
    return res;
}

// Element wise difference between two arrays (of the same size)
function ta_ARR_DIFF(a, b) {
    res = [];
    for (i = 0; i < a.length; i++) {
        res.push({time: a[i].time, value: a[i].value - b[i].value});
    }
    return res;
}

// Calculates SMA
function ta_SMA(src, len) {
    res_ = [];
    for (i = 0; i < src.length; i++) {
        time_ = src[i]['time'];
        if (i < len - 1) {
            res_.push({ time: time_, value: undefined });
        } else {
            val = ta_SUM(src.slice(i + 1 - len, i + 1)) / len;
            res_.push({ time: time_, value: val });
        }
    }
    return res_;
}

// Calculates EMA
function ta_EMA(src, len) {
    var k = 2 / (len + 1);
    res_ = [src[0]];
    for (var i = 1; i < src.length; i++) {
        v_ = src[i]['value'] * k + res_[i - 1]['value'] * (1 - k);
        res_.push({'time': src[i]['time'], 'value': v_});
    }
    return res_;
}

// Format value as volume
function formatVolume(val) {
    if (val / 1000000000000 >= 1) {
        return String(Math.round(val / 1000000000000 * 100) / 100) + 'T';
    } else if (val / 1000000000 >= 1) {
        return String(Math.round(val / 1000000000 * 100) / 100) + 'B';
    } else if (val / 1000000 >= 1) {
        return String(Math.round(val / 1000000 * 100) / 100) + 'M';
    } else if (val / 1000 >= 1) {
        return String(Math.round(val / 1000 * 100) / 100) + 'K';
    } else {
        return String(Math.round(val * 100) / 100);
    }
}   

// Resize price scales
function resizePriceScales(chart, show=0) {
    // Heights of different indicators
    heights = {
        'vol': show == 0 ? ($('#ind-vol .visibility').hasClass('yes') ? 0.1 : 0.04) : (show == 1 ? 0.1 : 0.04), 
        'macd': show == 0 ? ($('#ind-macd .visibility').hasClass('yes') ? 0.1 : 0.04) : (show == 1 ? 0.1 : 0.04), 
        'rsi': show == 0 ? ($('#ind-rsi .visibility').hasClass('yes') ? 0.1 : 0.04) : (show == 1 ? 0.1 : 0.04)
    }

    // Check what indicators are on chart
    inds = [];
    ms_height = 0.0;
    ma_ribbon_present = false;
    $('.ind').each(function(i, el) {
        id_ = $(el).attr('id').replace('ind-', '');
        if (id_ != 'ma-ribbon' && id_ != 'vrvp') {
            inds.push(id_);
            // Calculate height for main series
            ms_height += heights[id_] + 0.04;
        }
        if (id_ == 'ma-ribbon') {
            ma_ribbon_present = true;
        }
    })    
    ms_height += 0.005;
    main_pane_height = 1 - ms_height;

    // Set margins for main series
    msps = chart.priceScale('right');
    msps.applyOptions({
        scaleMargins: {
            top: 0.02,
            bottom: ms_height,
        }
    })

    // Set position of VRVP indicator UI
    $('#ind-vrvp > span:first-of-type').css('top', ma_ribbon_present ? '172px' : '138px');

    // Set position of drawing edit UI
    $('#draw-edit').css('bottom', 'calc(' + String(Math.round(ms_height * 100)) + '% + 20px)');

    // Find width of price scale
    rpsw = $('#chart table tr:nth-child(1) td:nth-child(3)').width() - 4;

    // Set margins for each price scale
    last_bot = ms_height;
    for (i = 0; i < inds.length; i++) {
        ps = chart.priceScale(inds[i]);
        top_ = 1 - last_bot + 0.04;
        bot_ = last_bot - 0.04 - heights[inds[i]] + (i == inds.length - 1 ? 0.005 : 0);
        ps.applyOptions({
            scaleMargins: {
                top: top_,
                bottom: bot_,
            }
        })

        $('#ind-' + inds[i] + ' > div.sep').css('top', String(Math.round(top_ * 100) - 5) + '%').css('width', 'calc(100% - ' + rpsw + 'px)');
        $('#ind-' + inds[i] + ' > span').css('top', String(Math.round(top_ * 100) - 3) + '%');

        last_bot = bot_;
    }
}

// Return top and bottom limits of price scale
function getPriceLimits() {
    pl = price_series.priceScale()._private__chartWidget._private__timeAxisWidget._private__chart._private__model._private__panes[0]._private__rightPriceScale._private__priceRange;
    return [pl['_private__maxValue'], pl['_private__minValue']];
}

// Get crosshair price
function getCurrentPrice() {
    return price_series.priceScale()._private__chartWidget._private__timeAxisWidget._private__chart._private__model._private__crosshair._private__price;
}

// Get series for point
function getPointSeries(chart) {
    return chart.addLineSeries({color: 'transparent', lineWidth: 0, lineStyle: 2, lastValueVisible: false, priceLineVisible: false, crosshairMarkerVisible: false});
}

// Set markers for each series in array
function selectDrawing(drawing, select=true) {
    if (drawing.type == 'fibret') {
        if (select) {
            for (i11_ = 0; i11_ < drawing.colors.length; i11_++) {
                drawing.colors[i11_] = drawing.colors[i11_].slice(0, 7) + 'ff';
            }
        } else {
            for (i11_ = 0; i11_ < drawing.colors.length; i11_++) {
                drawing.colors[i11_] = drawing.colors[i11_].slice(0, 7) + 'a5';
            }
        }
    } else {
        if (select) {
            drawing.color = drawing.color.slice(0, 7) + 'ff';
        } else {
            drawing.color = drawing.color.slice(0, 7) + 'a5';
        }
    }
    // Set drawing as selected
    drawing.selected = select;
}

// Check how many lines/fibret selected and display appropriate UI
function displayDrawEditUI() {
    dll5_ = drawings.length;
    // How many lines selected
    lines_selected = 0;
    line_color = null;
    line_style = null;
    line_width = null;
    // How many fibret selected
    fibret_selected = 0;
    fibret_colors = null;
    fibret_style = null;
    fibret_width = null;
    // Check what is selected to show appropriate UI
    for (i___ = 0; i___ < dll5_; i___++) {
        drawing_ = drawings[i___];
        if (drawing_.selected) {
            if (['vline', 'hline', 'trendline', 'brush'].includes(drawing_.type)) {
                lines_selected += 1;
                line_color = drawing_.color;
                line_style = drawing_.style;
                line_width = drawing_.width;
            } else if (drawing_.type == 'fibret') {
                fibret_selected += 1;
                fibret_colors = drawing_.colors;
                fibret_style = drawing_.style;
                fibret_width = drawing_.width;
                line_color = drawing_.colors[0];
                line_style = drawing_.styles[0];
                line_width = drawing_.widths[0];
            }
        }
    }
    // Remove alpha component
    if (line_color) {
        line_color = line_color.slice(0, 7);
    }
    // For UI of drawings
    if (lines_selected > 0 || fibret_selected > 0) {
        // Show the UI
        $('#draw-edit > div').removeClass('op0');
        // Setup the color, style and width inputs
        $('#draw-edit > div > label > input[type="color"]').val(line_color);
        $('#draw-edit > div > label').css('background-color', line_color);
        $('#draw-edit > div > select > option').prop('selected', '');
        $('#draw-edit > div > select > option[value="' + line_style + '"]').prop('selected', 'selected');
        $('#draw-edit > div > input').val(line_width);
        // If fibret is selected -> show also an icon of settings
        if (fibret_selected == 0) {
            $('#draw-edit > div > div.settings').addClass('op0');
        } else {
            $('#draw-edit > div > div.settings').removeClass('op0');
        }
    } else {
        $('#draw-edit > div').addClass('op0');
    }
}

// Test if price is on price_on (for checking if we clicked on an hline)
function testHLine(price, price_on, pldiff) {
    // Difference between clicked price and line price must not be > than 1%
    if (Math.abs(price - price_on) / pldiff <= 0.01) {
        return true;
    } else {
        return false;
    }
}

// Same as above but for vline
function testVLine(line_time, click_time, time_range, chart_width) {
    // Find how much time per 1 pixel
    tpp = (time_range.to - time_range.from) / chart_width;
    // We take into account a clickable range of 5px
    return (click_time >= line_time - tpp * 5) && (click_time <= line_time + tpp * 5);
}

function testTrendLine(time1, price1, time2, price2, time, price, bar_range) {
    // Find min/max time and price
    min_price = Math.min(price1, price2);   
    max_price = Math.max(price1, price2);
    min_time = Math.min(time1, time2);   
    max_time = Math.max(time1, time2);
    // Check if clicked point is within the time and price of line
    if (time >= min_time && time <= max_time && price >= min_price && price <= max_price) {
        price1 = price_series.priceToCoordinate(price1);
        price2 = price_series.priceToCoordinate(price2);
        price = price_series.priceToCoordinate(price);
        time1 = chart.timeScale().timeToCoordinate(time1);
        time2 = chart.timeScale().timeToCoordinate(time2);
        time = chart.timeScale().timeToCoordinate(time);
        // Check if clicked point is on the line
        dxc = time - time1;
        dyc = price - price1;
        dxl = time2 - time1;
        dyl = price2 - price1;
        cross = dxc * dyl - dyc * dxl;
        thr = (bar_range.to - bar_range.from) / 100 * 5000;
        return Math.abs(cross) <= Math.min(5000, Math.max(500, thr));
    } else {
        return false;
    }
}

function testBrush(init_point, bdata, x_, y_) {
    canvas_ = chart._private__chartWidget._private__paneWidgets[0]._private__canvasBinding.canvas;
    pixelRatio = canvas_.ownerDocument && canvas_.ownerDocument.defaultView && canvas_.ownerDocument.defaultView.devicePixelRatio || 1;
    // Get x axis K
    var bs = chart._private__chartWidget._private__paneWidgets[0]._private__state._private__model._private__timeScale._private__barSpacing;
    let xk = bs / init_point.xk;
    // Get y axis K
    plimits = getPriceLimits();
    pldiff = plimits[0] - plimits[1];
    let xy = pldiff / init_point.xy;
    // 
    x_ = x_ * pixelRatio;
    y_ = y_ * pixelRatio;
    let cox = chart.timeScale().timeToCoordinate(init_point.time) * pixelRatio;
    let coy = price_series.priceToCoordinate(init_point.value) * pixelRatio;
    let fx = bdata[0].x;
    let fy = bdata[0].y;
    var last_dx = cox;
    var last_dy = coy;
    for (var ij2 = 1; ij2 < bdata.length; ij2++) {
        let dx = cox - (fx - bdata[ij2].x) * pixelRatio * xk;
        let dy = coy - (fy - bdata[ij2].y) * pixelRatio / xy;
        //
        miny = Math.min(dy, last_dy) - 10;   
        maxy = Math.max(dy, last_dy) + 10;
        minx = Math.min(dx, last_dx) - 10;   
        maxx = Math.max(dx, last_dx) + 10;
        //
        if (x_ >= minx && x_ <= maxx && y_ >= miny && y_ <= maxy) {
            dxc = x_ - dx;
            dyc = y_ - dy;
            dxl = last_dx - dx;
            dyl = last_dy - dy;
            cross = dxc * dyl - dyc * dxl;
            if (Math.abs(cross) <= 5000) {
                return true;
            }
        }
        //
        last_dx = dx;
        last_dy = dy;
    }
    return false;
}

// Hide/show drawings on chart
function changeVisibilityDrawings(show=true, selected=false, deselect=true) {
    dll1_ = drawings.length;
    for (i__ = 0; i__ < dll1_; i__++) {
        drawing = drawings[i__];
        if (selected ? drawing.selected : true) {
            // Change property
            drawing.visible = show;
            // Deselect drawing
            if (deselect) {
                selectDrawing(drawing, false);
            }
        }
    }
}

// Delete drawings from chart
function deleteDrawings(selected=false) {
    dll2_ = drawings.length;
    for_del = [];
    for (i__ = 0; i__ < dll2_; i__++) {
        drawing = drawings[i__];
        if (selected ? drawing.selected : true) {
            for_del.push(drawing);
        }
    }
    if (!selected) {
        drawings = [];
    } else {
        drawings = drawings.filter(item => !for_del.includes(item));
        for_del = [];
    }
}

// Called when color input is changed
function st_FibretLevel_color_change(this_) {
    this_.parentNode.style.backgroundColor = this_.value;
}

// Called when we click on New Level
function st_FibretLevel_Add(this_) {
    n = String($(this_).parent().parent().find('.inps > div:not(.op0)').length + 1);
    h = '<div class="fr jb mt20"><div class="title" style="margin-top: 9px; white-space: nowrap">Level</div><div class="fr ml20"><input class="mr10" type="number" value="2" style="width: 110px"><label style="background-color: #5C7AFF" class="mr10"><input onchange="st_FibretLevel_color_change(this)" type="color" value="#5C7AFF"></label><select class="mr10"><option value="0">Solid</option><option value="1">Dotted</option><option value="2" selected="selected">Dashed</option></select><input type="number" value="2" style="width: 75px"><div class="remove ml10" onclick="st_MA_Ribbon_remove_row(this)"><img onclick="st_FibretLevel_remove_row(this)" class="cf-red" src="/static/icons/cross.png" width="20" height="20" style="cursor: pointer; margin-top: 9px"></div></div></div>';
    $(this_).closest('.inputs').find('.inps').append(h);
    $(this_).parent().parent().find('.inps > div .remove').removeClass('op0');
}

// Called when we click on remove level row
function st_FibretLevel_remove_row(this_) {
    par = $(this_).parent().parent().parent().parent();
    if (par.find('> div').length > 4) {
        $(this_).parent().parent().parent().remove();
        if (par.find('> div').length == 4) {
            par.find('> div .remove').addClass('op0');
        } else {
            par.find('> div .remove').removeClass('op0');
        }
    } 
}

// Called when we click on settings icon when any fibret is selected
function drawEditCreateFibretUI(this_) {
    // Fill inputs
    for (ijj1 = 0; ijj1 < drawings.length; ijj1++) {
        drawing = drawings[ijj1];
        if (drawing.type == 'fibret' && drawing.selected) {
            $('#draw-edit-inputs .inps').html('');
            for (jjj1 = 0; jjj1 < drawing.colors.length; jjj1++) {
                // Color
                col = drawing.colors[jjj1].slice(0, 7);
                // Width
                width_ = drawing.widths[jjj1];
                // Style
                style_ = drawing.styles[jjj1];
                options_ = '<option' + ((style_ == '0') ? ' selected="selected"' : '') + ' value="0">Solid</option>';
                options_ += '<option' + ((style_ == '1') ? ' selected="selected"' : '') + ' value="1">Dotted</option>';
                options_ += '<option' + ((style_ == '2') ? ' selected="selected"' : '') + ' value="2">Dashed</option>';
                // Trendline does not have level input
                lvl_input = (jjj1 == 0) ? '' : '<input class="mr10" type="number" value="' + drawing.levels[jjj1 - 1] + '" style="width: 110px">';
                // Title
                title_ = (jjj1 == 0) ? 'Trendline' : 'Level';
                // Trendline can't be removed
                remove_onclick_ = (jjj1 == 0) ? '' : ' onclick="st_FibretLevel_remove_row(this)"';
                dh_ = (jjj1 == 0) ? 'visibility: hidden' : '';
                // Add new element
                h = '<div class="fr jb mt20"><div class="title" style="margin-top: 9px; white-space: nowrap">' + title_ + '</div><div class="fr ml20">' + lvl_input + '<label style="background-color: ' + col + '" class="mr10"><input onchange="st_FibretLevel_color_change(this)" value="' + col + '" type="color"></label><select class="mr10">' + options_ + '</select><input type="number" value="' + width_ + '" style="width: 75px"><div class="remove ml10"><img' + remove_onclick_ + ' class="cf-red" src="/static/icons/cross.png" width="20" height="20" style="cursor: pointer; margin-top: 9px;' + dh_ + '"></div></div></div>';
                $('#draw-edit-inputs .inps').append(h);
            }   
            // We take all the inputs from first fibret (in case more than 1 are selected)
            break;
        }
    }
    // Show the popup
    $('#draw-edit-inputs').removeClass('op0');
}

// Called when we click on Save
function st_FibretLevel_save() {
    // Gather data
    data_ = [];
    $('#draw-edit-inputs .inps > div').each(function(i, el) {
        // Level
        lvl = (i == 0) ? undefined : $(el).find('input[type="number"]:first-child').val();
        // Get color
        col_ = $(el).find('input[type="color"]').val();
        // Style
        style_ = String($(el).find('select > option:selected').attr('value'));
        // Width
        width_ = $(el).find('input[type="number"]:not(.mr10)').val();
        // Add to data
        data_.push({
            color: col_, 
            level: lvl,
            style: style_,
            width: width_
        })
    }); 
    for (jjj2 = 0; jjj2 < drawings.length; jjj2++) {
        drawing = drawings[jjj2];
        if (drawing.type == 'fibret' && drawing.selected) {
            drawing.colors = [data_[0].color];
            drawing.styles = [data_[0].style];
            drawing.widths = [data_[0].width];
            drawing.levels = [];
            drawing.prices = [];
            //
            t1_ = Math.min(drawing.time1, drawing.time2);
            t2_ = Math.max(drawing.time1, drawing.time2);
            //
            for (iii1 = 1; iii1 < data_.length; iii1++) {
                // Calculate price
                new_lvl = drawing.price2 + (drawing.price1 - drawing.price2) * data_[iii1].level;
                drawing.prices.push(new_lvl);
                // Change properties
                drawing.colors.push(data_[iii1].color);
                drawing.styles.push(data_[iii1].style);
                drawing.widths.push(data_[iii1].width);
                drawing.levels.push(data_[iii1].level);
            }
        }
    }
    
    // Close popup
    $('#draw-edit-inputs').addClass('op0');
}