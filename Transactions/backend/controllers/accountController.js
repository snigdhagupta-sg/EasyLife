const Account = require("../models/accountnumbers");

exports.addAccountNumber = async (req, res) => {
  try {
    const user_id = req.cookies.user_id;
    const { account_number } = req.body;

    // User authentication check
    if (!user_id) {
      return res.status(401).json({ message: "Not authenticated" });
    }

    // Account number validation
    if (!account_number) {
      return res.status(400).json({ message: "Account number required" });
    }

    // Duplicate account check
    const existing = await Account.findOne({ user_id, account_number });
    if (existing) {
      return res.status(409).json({ message: "This account already exists for this user!" });
    }

    // Create new account
    await Account.create({ user_id, account_number });

    // Success response
    res.status(201).json({ success: true, message: "Account added" });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: "Could not add account" });
  }
};


exports.deleteAccountNumber = async (req, res) => {
  try {
    const user_id = req.cookies.user_id;
    const { account_number } = req.body;

    if (!user_id) return res.status(401).json({ message: "Not authenticated" });

    await Account.deleteOne({ user_id, account_number });

    res.json({ success: true, message: "Account deleted" });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: "Deletion failed" });
  }
};

exports.getAccountNumbers = async (req, res) => {
  try {
    const user_id = req.cookies.user_id;

    if (!user_id) return res.status(401).json({ message: "Not authenticated" });

    const accounts = await Account.find({ user_id });

    res.json({ success: true, accounts });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false });
  }
};
