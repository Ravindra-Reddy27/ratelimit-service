// Switch to our specific database
db = db.getSiblingDB('ratelimitdb');

// Create the clients collection
db.createCollection('clients');

// Insert 3 test clients with different limits
db.clients.insertMany([
  {
    clientId: "client-basic",
    hashedApiKey: "dummy-hash-1", // We will implement real hashing later
    maxRequests: 5,               // 5 requests allowed...
    windowSeconds: 60,            // ...every 60 seconds
    createdAt: new Date(),
    updatedAt: new Date()
  },
  {
    clientId: "client-pro",
    hashedApiKey: "dummy-hash-2",
    maxRequests: 50,
    windowSeconds: 60,
    createdAt: new Date(),
    updatedAt: new Date()
  },
  {
    clientId: "client-unlimited",
    hashedApiKey: "dummy-hash-3",
    maxRequests: 1000,
    windowSeconds: 60,
    createdAt: new Date(),
    updatedAt: new Date()
  }
]);

print("Database seeded successfully with 3 test clients!");