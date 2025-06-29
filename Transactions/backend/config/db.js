require ('dotenv').config();
const mongoose = require ('mongoose');
async function ConnectMongo(){
    try{
        await mongoose.connect(process.env.MONGODB_URL);
        console.log('Connected to MongoDB!');
    }
    catch(error){
        console.log('Not connected to MongoDB!');
        console.log(error);
        process.exit(1);
    }
}
module.exports = ConnectMongo;