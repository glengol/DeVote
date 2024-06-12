// Connect to admin database
db = db.getSiblingDB('admin');

// Create user
db.createUser({
    user: 'root',
    pwd: 'root',
    roles: [{ role: 'readWriteAnyDatabase', db: 'admin' }]
});
