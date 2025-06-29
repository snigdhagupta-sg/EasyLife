const express = require("express");
const router = express.Router();
const {
  addAccountNumber,
  deleteAccountNumber,
  getAccountNumbers
} = require("../controllers/accountController");

router.post("/add", addAccountNumber);
router.delete("/delete", deleteAccountNumber);
router.get("/all", getAccountNumbers);

module.exports = router;
