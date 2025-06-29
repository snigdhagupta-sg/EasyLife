const express = require("express");
const router = express.Router();
const {
  getTransactions,
  addCashTransaction
} = require("../controllers/transactionController");

router.get("/all", getTransactions);
router.post("/add-cash", addCashTransaction);

module.exports = router;
