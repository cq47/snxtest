function generateSession(is_chart=false) {
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for (var i = 0; i < 12; i++ ) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return (is_chart ? 'cs_' : 'qs') + result;
}

function prependHeader(st) {
    return '~m~' + String(st.length) + '~m~' + st;
}

function constructMessage(func, paramList) {
    return JSON.stringify({'m': func, 'p': paramList})
}

function createMessage(func, paramList) {
    return prependHeader(constructMessage(func, paramList))
}

function sendMessage(ws, func, args) {
    ws.send(createMessage(func, args));
}