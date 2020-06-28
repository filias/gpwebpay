(function () {
  const toggleShoppingList = () => {
    const shopping_list = document.querySelector(".shopping-list");
    const shopping_cart_icon = document.querySelector(".shopping-cart");

    shopping_cart_icon.addEventListener("click", function () {
      shopping_list.classList.toggle("hide");
    });
  };
  toggleShoppingList();

  const shoppingBtns = document.querySelectorAll(".products__btn");

  //array of prices
  const productsInTheCart = [];

  shoppingBtns.forEach(function (elem) {
    elem.addEventListener("click", function (event) {
      if (event.target.parentElement.classList.contains("products__btn")) {
        let price = parseFloat(this.dataset.price);
        productsInTheCart.push(price);
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

const proceed_payment = () => {
  let finalAmount = document.getElementById("total").innerText;

  let amountObject = {
    amount: finalAmount,
  };

  fetch(`${window.origin}/pay`, {
    method: "POST",
    credentials: "include",
    body: JSON.stringify(amountObject),
    cache: "no-cache",
    // mode: "no-cors",
    headers: new Headers({
      "content-type": "application/json",
    }),
  })
    .then(function (response) {
      if (response.status !== 200) {
        console.log(`There is an error! Status code: ${response.status}`);
        return;
      }
      response.json().then(function (data) {
        console.log(data);
      });
    })
    .catch(function (error) {
      console.log("Fetch error: " + error);
    });
};
