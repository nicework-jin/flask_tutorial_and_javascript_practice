function updateLikeCnt(){
    const post_id = likeBtn.getAttribute("value");
        $.ajax({
            type : 'POST',
            url : 'http://127.0.0.1:5000/like',
            data : {
                post_id:post_id,
            },
            dataType : 'JSON',
            success : function(result){
                document.getElementById("likes").innerHTML = result;
            },
            error : function(error){
                alert(error);
            }
        });
}

function createCommentHTML(comment){
    return `<tr>
                <td> ${comment["number"]} </td>
                <td> ${comment["username"]} </td>
                <td> ${comment["body"]} </td>
            </tr>`}

function addComment(){
    const commentInput = document.getElementById("commentInput");
    post_id = commentInput.getAttribute("data-post-id");
    body = commentInput.value;

    $.ajax({
        type : 'POST',
        url : 'http://127.0.0.1:5000/create_comment',
        data : {
            post_id:post_id,
            body:body,
        },
        dataType : 'JSON',
            success : function(result){
            const container = document.getElementById("commentShow");
            container.innerHTML = result['comment'].map(comment => createCommentHTML(comment)).join('');
        },
        error : function(error){
            alert(error);
        }
    });
}


const likeBtn = document.querySelector('.likeBtn');
likeBtn.addEventListener('click', () => {
    updateLikeCnt();
    likeBtn.classList.toggle('clicked');
});

const commentSubmit = document.getElementById('commentSubmit');
commentSubmit.addEventListener('click', () =>{
    addComment();
    document.getElementById('commentForm').reset();
})


function pagePerRows(idx, rows, rowsPerPage){
    let start = (idx - 1) * rowsPerPage;
    let end = start + rowsPerPage;
    console.log(rows);
    rows.hide();
    rows.slice(start, end).show();
}

function pagination(comments){
    const rowsPerPage = 5;
    const rows = $('#commentShow tr');
    const rowCount = rows.length;

    const pageCount = Math.ceil(rowCount/rowsPerPage);
    pageNumbers = $('.pagination');

    for (let i = 1; i <= pageCount; i++){
        pageNumbers.append('<li><a href="#" onclick=pagePerRows('+i+')>' + i + '</a></li>');
        pageNumbers.find('li:nth-child('+i+')').addClass('active');
    }
    pagePerRows(1, rows, rowsPerPage);
}

const rows = $('#postLoad');
console.log(rows.length);
