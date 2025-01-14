import brownie
from brownie import Contract
# TODO: Add tests that show proper migration of the strategy to a newer one
#       Use another copy of the strategy to simulate the migration
#       Show that nothing is lost!


def test_migration(token, vault, chain, strategy, Strategy, strategist, whale, gov, yfibank, bank, router):
    
    with brownie.reverts("Strategy already initialized"):
        strategy.initialize(vault, strategist, strategist, strategist, yfibank, router, token, bank)

    # Deposit to the vault and harvest
    amount = 1 *1e18
    bbefore= token.balanceOf(whale)

    token.approve(vault.address, amount, {"from": whale})
    vault.deposit(amount, {"from": whale})
    strategy.harvest()
    
    tx = strategy.cloneStrategy(vault, yfibank, router, token, bank)
    

    # migrate to a new strategy
    new_strategy = Strategy.at(tx.return_value)


    vault.migrateStrategy(strategy, new_strategy, {"from": gov})
    assert new_strategy.estimatedTotalAssets() >= amount
    assert strategy.estimatedTotalAssets() == 0

    new_strategy.harvest({"from": gov})


    chain.mine(20)
    chain.sleep(2000)
    new_strategy.harvest({"from": gov})
    chain.sleep(60000)
    vault.withdraw({"from": whale})
    assert token.balanceOf(whale) > bbefore





