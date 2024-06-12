describe('voting page', () => {
  it('shows name page', () => {
    cy.visit('http://localhost:5000')
  })
  it('shows voting options', () => {
    cy.visit('http://localhost:5000')
    cy.get("#name").type("test{enter}")
    cy.get("#AWS").click()
    cy.get("#YAML").click()
  })
  it('can save vote', () => {
    cy.visit('http://localhost:5000')
    cy.get("#name").type("test{enter}")
    cy.get("#AWS").click()
    cy.get("#YAML").click()
    cy.get("#submit_vote").click()
    cy.get('.back-button').click()
    cy.contains("Enter your name")
  })
})