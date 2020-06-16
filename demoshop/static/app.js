(function () {
  const toggleShoppingList = () => {
    const shopping_list = document.querySelector(".shopping-list");
    const shopping_cart_icon = document.querySelector(".shopping-cart");

    shopping_cart_icon.addEventListener("click", function () {
      console.log(shopping_cart_icon);
      console.log(shopping_list);
      shopping_list.classList.toggle("hide");
    });
  };
  toggleShoppingList();

  const shoppingBtns = document.querySelectorAll(".products__btn");
  console.log(shoppingBtns);

  //array of prices
  const productsInTheCart = [];

  shoppingBtns.forEach(function (elem) {
    elem.addEventListener("click", function (event) {
      if (event.target.parentElement.classList.contains("products__btn")) {
        let price = parseFloat(this.dataset.price);
        productsInTheCart.push(price);
        console.log(productsInTheCart);
      }
      let total = sumPrice().toFixed(2);
      updateTotal(total);
    });
  });

  const sumPrice = () => {
    return productsInTheCart.reduce(function (total, item) {
      total += item;
      return total;
    }, 0);
  };

  const updateTotal = (total) => {
    let totalContainer = document.getElementById("total");
    totalContainer.innerText = total;
  };
})();
