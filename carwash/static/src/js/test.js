$(document).ready(function() {
    // input alanında her değişiklik olduğunda çalışacak
    $(document).on('input', '.o_form_view .delivery_details input', function() {
        var inputValue = $(this).val();  // input değerini al
        console.log(inputValue);  // değeri konsola yazdır
        $('#test_div').text(inputValue);  // değeri test_div id'li div içine yazdır
    });

    // Sayfa yüklendiğinde mevcut değeri al ve yazdır
    var initialValue = $('.o_form_view .delivery_details input').val();
    $('#test_div').text(initialValue);
});