
local mymodule = {}

function mymodule.SetCoordinates(character)
    local facing = GetPlayerFacing();
    local pitch = GetUnitPitch(character);
    local x, y = GetPlayerMapPosition(character);
    local x1, x2 = math.modf(x * 255)
    local y1, y2 = math.modf(y * 255)
    if character == "player" then
        AssistantCoordinatesSquare1.texture:SetTexture(x1 / 255, x2, facing / 7)
        AssistantCoordinatesSquare2.texture:SetTexture(y1 / 255, y2, pitch / 4 + 0.5)
    else
        MainCharacterCoordinatesSquare1.texture:SetTexture(x1 / 255, x2, facing)
        MainCharacterCoordinatesSquare2.texture:SetTexture(y1 / 255, y2, pitch)
    end
end

function mymodule.SetConditionStatus(character)
    local inCombat = 0
    if UnitAffectingCombat(character) then
        inCombat = 1
    end
    local healthPercent = UnitHealth(character) / UnitHealthMax(character)

    -- Function to accept party with delay
function mymodule.AcceptPartyWithDelay(seconds)
    AcceptPartyLogicFrame:SetScript("OnUpdate", function(self, elapsed)
        if seconds > 0 then
            seconds = seconds - elapsed
        else
            AcceptGroup()
            AcceptPartyLogicFrame:SetScript("OnUpdate", nil)  -- Stop the timer
        end
    end)
end

    if character == "player" then
        AssistantConditionSquare1.texture:SetTexture(inCombat, healthPercent, 0)
    else
        MainCharacterConditionSquare1.texture:SetTexture(inCombat, healthPercent, 0)
    end
end

--function MainCharacterConditionStatus(character)
--    local inCombat = 0
--    if UnitAffectingCombat(character) then
--        inCombat = 1
--    end
--    local healthPercent = UnitHealth(character)/UnitHealthMax(character)
--    MainCharacterConditionSquare1.texture:SetTexture(inCombat, healthPercent, 0)
--end

-- Function to accept party with delay
function mymodule.AcceptPartyWithDelay(seconds)
    AcceptPartyLogicFrame:SetScript("OnUpdate", function(self, elapsed)
        if seconds > 0 then
            seconds = seconds - elapsed
        else
            AcceptGroup()
            AcceptPartyLogicFrame:SetScript("OnUpdate", nil)  -- Stop the timer
        end
    end)
end

-- Function to display the targets of party members
function mymodule.ShowPartyMembersTargets()
    local unit = "party1"
    if UnitExists(unit) then
        local targetName = UnitName(unit .. "target")
        local targetGUID = tonumber(UnitGUID(unit .. "target"), 16)
        if targetName then
            print(UnitName(unit) .. "'s target: " .. targetName)
            print(UnitName(unit) .. "'s target: " .. targetGUID)
        else
            print(UnitName(unit) .. " has no target.")
        end
    end
end