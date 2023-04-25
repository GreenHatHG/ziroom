// 获取所有class为checkbox-group的元素
var checkboxGroups = document.getElementsByClassName("checkbox-group");

// 定义一个数组用于存储提取出来的数据
var result = {};

// 遍历每个checkbox-group元素
for (var i = 0; i < checkboxGroups.length; i++) {
    // 获取当前checkbox-group元素下的所有a标签
    var checkboxes = checkboxGroups[i].getElementsByTagName("a");
    // 遍历每个a标签
    for (var j = 0; j < checkboxes.length; j++) {
        // 获取当前a标签的href属性和文本内容
        var href = checkboxes[j].getAttribute("href");
        var text = checkboxes[j].textContent;
        // 将获取到的数据存储到结果数组中
        result[text] = href;
    }
}

// 输出结果数组
console.log(JSON.stringify(result));