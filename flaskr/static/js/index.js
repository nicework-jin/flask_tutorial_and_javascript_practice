function createPageHTML(){
    for (let i = 1; i < totPage + 1; i++){
        page.append('<li><a href="#" onclick="showRowsPerPage(' + i + ')"> ' + i + ' </a></li>');
    }
}

function showRowsPerPage(idx){
    const start = (idx - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    contents.hide();
    contents.slice(start, end).show();
}

const numRows = $('.post header').length;
const rowsPerPage = 5;
const totPage = Math.ceil(numRows/rowsPerPage);

// 페이지 번호 만들기
const page = $('.pagination');
createPageHTML();

// rowsPerPage 개수 만큼 화면에 보이도록.
const contents = $('.post');
showRowsPerPage(1);